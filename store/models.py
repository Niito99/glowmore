from django.db import models
from cloudinary.models import CloudinaryField

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Skin Care', 'Skin Care'),
        ('Body Care', 'Body Care'),
        ('Lip Care', 'Lip Care'),
        ('General Goods', 'General Goods'),
        ('Beauty tools and Accessories', 'Beauty tools and Accessories'),
        ('Oral Care', 'Oral Care'),
        ('Combo', 'Combo'),
        ('Glow Box', 'Glow Box'),
        ('Care Box', 'Care Box'),
        ('Birthday Package', 'Birthday Package'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_length=10, decimal_places=2, max_digits=10)
    original_price = models.DecimalField(max_length=10, decimal_places=2, max_digits=10, blank=True, null=True, help_text="If set higher than the price, it will show a SALE badge and crossed-out old price")
    stock = models.IntegerField(default=0)
    image = CloudinaryField('image', blank=True, null=True)
    
    has_size_options = models.BooleanField(default=False, help_text="Check this to offer Large, Medium, and Small sizes.")
    color_1 = models.CharField(max_length=50, blank=True, null=True)
    color_2 = models.CharField(max_length=50, blank=True, null=True)
    color_3 = models.CharField(max_length=50, blank=True, null=True)
    
    stock_large = models.IntegerField(default=0)
    stock_medium = models.IntegerField(default=0)
    stock_small = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.has_size_options:
            self.stock = self.stock_large + self.stock_medium + self.stock_small
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='photos', on_delete=models.CASCADE)
    image = CloudinaryField('image')

    def __str__(self):
        return f"{self.product.name} Image"

class Order(models.Model):
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paystack_reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
