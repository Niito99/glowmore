from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import Product, Order, OrderItem
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .forms import ProductForm

def product_list(request):
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')
    search = request.GET.get('search')

    products = Product.objects.all()

    if category:
        products = products.filter(category=category)
    
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) | 
            Q(category__icontains=search)
        )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    categories = Product.CATEGORY_CHOICES
    
    # We define new arrivals as latest 10 products
    new_arrivals = Product.objects.all().order_by('-created_at')[:10]
    
    # We define best sellers as 10 products based on id sorting for now as a mock metric
    best_sellers = Product.objects.all()[:10]
    
    return render(request, 'store/index.html', {
        'products': products,
        'categories': categories,
        'current_category': category,
        'new_arrivals': new_arrivals,
        'best_sellers': best_sellers,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    
    if product.stock <= 0:
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('product_detail', product_id=product.id)
    
    cart = request.session.get('cart', {})
    
    # Generate unique key for variations
    cart_key = str(product_id)
    if size:
        cart_key += f"_{size}"
    if color:
        cart_key += f"_{color}"
    
    if cart_key in cart:
        new_quantity = cart[cart_key]['quantity'] + quantity
        if new_quantity > product.stock:
            messages.error(request, f"Sorry, you can't add that many. Only {product.stock} available.")
            return redirect('product_detail', product_id=product.id)
            
        cart[cart_key]['quantity'] = new_quantity
    else:
        if quantity > product.stock:
            messages.error(request, f"Sorry, only {product.stock} available.")
            return redirect('product_detail', product_id=product.id)
            
        cart[cart_key] = {
            'product_id': product_id,
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
            'image': product.image.url,
            'size': size,
            'color': color
        }
    
    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart!")
    return redirect('cart_view')

def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})
    if cart_key in cart:
        name = cart[cart_key]['name']
        del cart[cart_key]
        request.session['cart'] = cart
        messages.info(request, f"{name} removed from cart.")
    return redirect('cart_view')

def update_cart(request, cart_key):
    quantity = int(request.POST.get('quantity', 1))
    cart = request.session.get('cart', {})
    
    if cart_key in cart:
        # Extract product ID to check stock for updates
        product_id = cart[cart_key]['product_id']
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > product.stock:
            messages.error(request, f"Cannot update. Only {product.stock} available in stock.")
        elif quantity > 0:
            cart[cart_key]['quantity'] = quantity
        else:
            del cart[cart_key]
            
        request.session['cart'] = cart
    
    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', {})
    total = 0
    for item in cart.values():
        total += float(item['price']) * item['quantity']
    
    return render(request, 'store/cart.html', {
        'cart': cart,
        'total': total
    })

def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
    
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    
    if request.method == 'POST':
        # This will be handled by AJAX/Paystack callback usually, 
        # but we can collect details here if needed before launching Paystack.
        pass

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'total': total,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
    })

@csrf_exempt
def verify_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    res_data = response.json()
    
    if res_data.get('status') and res_data['data']['status'] == 'success':
        # Payment successful, create order
        data = res_data['data']
        customer_info = data.get('metadata', {}).get('custom_fields', [])
        
        # Extract fields from metadata passed via Paystack
        metadata = data.get('metadata', {})
        name = metadata.get('full_name', 'Unknown')
        phone = metadata.get('phone', '')
        address = metadata.get('address', '')
        email = data['customer']['email']
        total_amount = data['amount'] / 100 # Convert kobo to GHS
        
        order = Order.objects.create(
            customer_name=name,
            email=email,
            phone=phone,
            address=address,
            total_amount=total_amount,
            paystack_reference=reference,
            is_paid=True
        )
        
        # Create Order Items
        cart = request.session.get('cart', {})
        order_items_summary = ""
        for cart_key, item in cart.items():
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                unit_price=item['price']
            )
            
            # Format variations for email
            variation_text = []
            if item.get('size'):
                variation_text.append(f"Size: {item['size']}")
            if item.get('color'):
                variation_text.append(f"Color: {item['color']}")
            
            variation_str = f" ({', '.join(variation_text)})" if variation_text else ""
            
            order_items_summary += f"- {product.name}{variation_str} x {item['quantity']} (₵{item['price']})\n"
            # Update stock
            product.stock -= item['quantity']
            product.save()

        # Trigger Web3Forms Email
        web3_url = "https://api.web3forms.com/submit"
        web3_data = {
            "access_key": settings.WEB3FORMS_ACCESS_KEY,
            "subject": f"New GlowMore Order — {order.id}",
            "from_name": "GlowMore Store",
            "email": email,
            "message": f"Hello {name},\n\nThank you for your order!\n\nOrder Summary:\n{order_items_summary}\nTotal Paid: ₵{total_amount}\nDelivery Address: {address}\n\nWe will contact you shortly for delivery.",
        }
        web3_response = requests.post(web3_url, json=web3_data)
        print("Web3Forms Response:", web3_response.text)

        # Clear cart
        request.session['cart'] = {}
        
        return JsonResponse({'status': 'verified', 'order_id': order.id})
    
    return JsonResponse({'status': 'failed'}, status=400)

def order_confirmed(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_confirmed.html', {'order': order})

# Dashboard Views
def staff_check(user):
    return user.is_staff

@login_required
@user_passes_test(staff_check)
def dashboard_home(request):
    total_orders = Order.objects.count()
    total_sales = sum(o.total_amount for o in Order.objects.filter(is_paid=True))
    recent_orders = Order.objects.order_by('-created_at')[:5]
    product_count = Product.objects.count()
    
    return render(request, 'store/dashboard/home.html', {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'product_count': product_count,
    })

@login_required
@user_passes_test(staff_check)
def dashboard_products(request):
    products = Product.objects.all()
    return render(request, 'store/dashboard/products.html', {'products': products})

@login_required
@user_passes_test(staff_check)
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('photos')
            if images:
                from .models import ProductImage
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Product created successfully!")
            return redirect('dashboard_products')
    else:
        form = ProductForm()
    return render(request, 'store/dashboard/product_form.html', {'form': form, 'title': 'Add New Product'})

@login_required
@user_passes_test(staff_check)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('photos')
            if images:
                from .models import ProductImage
                for img in images:
                    ProductImage.objects.create(product=product, image=img)
            messages.success(request, "Product updated successfully!")
            return redirect('dashboard_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/dashboard/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@user_passes_test(staff_check)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('dashboard_products')
    return render(request, 'store/dashboard/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(staff_check)
def dashboard_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/dashboard/orders.html', {'orders': orders})

@login_required
@user_passes_test(staff_check)
def dashboard_messages(request):
    from .models import ContactMessage
    inquiries = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'store/dashboard/messages.html', {'inquiries': inquiries})

def owner_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard_home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/dashboard/login.html', {'form': form})

def owner_logout(request):
    logout(request)
    return redirect('product_list')

def about_view(request):
    return render(request, 'store/about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_body = request.POST.get('message')
        
        from .models import ContactMessage
        ContactMessage.objects.create(name=name, email=email, message=message_body)
        
        messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
        return redirect('contact')
        
    return render(request, 'store/contact.html')

def returns_view(request):
    return render(request, 'store/returns.html')

def faq_view(request):
    return render(request, 'store/faq.html')

def privacy_view(request):
    return render(request, 'store/privacy.html')

def terms_view(request):
    return render(request, 'store/terms.html')
