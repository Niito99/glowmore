from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'original_price', 'category', 'stock', 'image', 'has_size_options', 'color_1', 'color_2', 'color_3', 'stock_large', 'stock_medium', 'stock_small']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input'}),
            'original_price': forms.NumberInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'stock': forms.NumberInput(attrs={'class': 'form-input'}),
            'stock_large': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity'}),
            'stock_medium': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity'}),
            'stock_small': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Quantity'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
            'has_size_options': forms.CheckboxInput(attrs={'class': 'form-input-checkbox'}),
            'color_1': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Red'}),
            'color_2': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Blue'}),
            'color_3': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Green'}),
        }
