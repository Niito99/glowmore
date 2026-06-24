from django.core.management.base import BaseCommand
from store.models import Product
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Seeds the database with sample products'

    def handle(self, *args, **kwargs):
        products = [
            {
                'name': 'Lavender Face Cream',
                'category': 'Skincare',
                'description': 'A soothing face cream infused with organic lavender oils for overnight hydration.',
                'price': 120.00,
                'stock': 50,
            },
            {
                'name': 'Vitamin C Serum',
                'category': 'Skincare',
                'description': 'Brighten your skin with our potent Vitamin C serum. Perfect for daily use.',
                'price': 150.00,
                'stock': 30,
            },
            {
                'name': 'Violet Matte Lipstick',
                'category': 'Makeup',
                'description': 'Long-lasting matte lipstick in a stunning deep violet shade.',
                'price': 85.00,
                'stock': 100,
            },
            {
                'name': 'Radiant Foundation',
                'category': 'Makeup',
                'description': 'Lightweight foundation that provides a natural, glowing finish.',
                'price': 180.00,
                'stock': 40,
            },
            {
                'name': 'Argan Oil Shampoo',
                'category': 'Haircare',
                'description': 'Nourishing shampoo with Moroccan argan oil for silky smooth hair.',
                'price': 95.00,
                'stock': 60,
            },
            {
                'name': 'Silk Conditioner',
                'category': 'Haircare',
                'description': 'Deeply hydrate your hair with our signature silk protein conditioner.',
                'price': 90.00,
                'stock': 60,
            },
            {
                'name': 'Midnight Rose Perfume',
                'category': 'Fragrance',
                'description': 'An enchanting floral fragrance with notes of damask rose and amber.',
                'price': 350.00,
                'stock': 20,
            },
            {
                'name': 'Citrus Bloom Mist',
                'category': 'Fragrance',
                'description': 'A refreshing body mist with zesty citrus and light floral undertones.',
                'price': 130.00,
                'stock': 75,
            },
        ]

        sample_image_path = 'media/products/sample.png'
        
        if not os.path.exists(sample_image_path):
            self.stdout.write(self.style.ERROR(f'Sample image not found at {sample_image_path}'))
            return

        for p_data in products:
            product, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'category': p_data['category'],
                    'description': p_data['description'],
                    'price': p_data['price'],
                    'stock': p_data['stock'],
                }
            )
            if created:
                with open(sample_image_path, 'rb') as f:
                    product.image.save(f'product_{product.id}.png', File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f'Created product: {product.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Product already exists: {product.name}'))
