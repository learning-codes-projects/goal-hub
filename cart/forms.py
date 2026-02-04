# cart/forms.py
from django import forms
from products.models import Product


class CartItemCreateForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        empty_label="Seleccioná un producto",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )


class CartItemUpdateForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=0,  # 0 = eliminar (UX común)
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
