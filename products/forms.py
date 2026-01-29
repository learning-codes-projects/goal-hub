from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    # Campo extra para pegar data-uri o base64

    class Meta:
        model = Product
        # incluimos photo (archivo) + photo_base64 (texto)
        fields = ["name", "description", "price", "stock", "is_active", "photo"]
