from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:cart_key>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('order-confirmed/', views.order_confirmed, name='order_confirmed'),
    
    # Dashboard
    path('owner/login/', views.owner_login, name='owner_login'),
    path('owner/logout/', views.owner_logout, name='owner_logout'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/products/', views.dashboard_products, name='dashboard_products'),
    path('dashboard/products/add/', views.product_create, name='product_create'),
    path('dashboard/products/edit/<int:pk>/', views.product_update, name='product_update'),
    path('dashboard/products/delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('dashboard/orders/', views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/messages/', views.dashboard_messages, name='dashboard_messages'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('returns/', views.returns_view, name='returns'),
    path('faq/', views.faq_view, name='faq'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
]
