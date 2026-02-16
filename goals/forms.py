# goals/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.utils.safestring import mark_safe
import base64

from products.models import Product
from .models import Goal, GoalProduct


class ProductSelectWithPrice(forms.Select):

    
    def render(self, name, value, attrs=None, renderer=None):

        if attrs is None:
            attrs = {}
        
        attrs.setdefault('class', 'form-select')
        
        # Obtener el HTML base del select
        html = ['<select name="%s"' % name]
        
        # Agregar atributos
        for key, val in attrs.items():
            if val:
                html.append(' %s="%s"' % (key, val))
        
        html.append('>')
        
        # Opción vacía
        html.append('<option value="">---------</option>')
        
        # Productos
        products = Product.objects.filter(is_active=True).values_list('id', 'name', 'price')
        for product_id, product_name, price in products:
            selected = ' selected' if str(value) == str(product_id) else ''
            html.append(
                '<option value="%s" data-price="%.2f"%s>%s</option>' 
                % (product_id, float(price), selected, product_name)
            )
        
        html.append('</select>')
        
        return mark_safe(''.join(html))


class GoalForm(forms.ModelForm):
    photo_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": "image/*"
        }),
        label="Foto del Objetivo"
    )

    class Meta:
        model = Goal
        fields = ["title", "motivo"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del objetivo"
            }),
            "motivo": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Describe por qué se necesita alcanzar este objetivo",
                "rows": 4
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Procesar el archivo de foto si existe
        photo_file = self.cleaned_data.get('photo_file')
        if photo_file:
            # Guardar en base64
            content = photo_file.read()
            instance.photo_b64 = base64.b64encode(content).decode('utf-8')
            instance.photo_mime = photo_file.content_type
        
        if commit:
            instance.save()
        return instance


class GoalProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        widget=ProductSelectWithPrice(attrs={"class": "form-select"}),
        label="Producto"
    )

    class Meta:
        model = GoalProduct
        fields = ["product", "goal_stock"]
        widgets = {
            "goal_stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Stock del objetivo",
                "min": "1"
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calcular unit_price automáticamente del producto
        if instance.product:
            instance.unit_price = instance.product.price
        if commit:
            instance.save()
        return instance


GoalProductFormSet = inlineformset_factory(
    Goal,
    GoalProduct,
    form=GoalProductForm,
    extra=3,
    can_delete=True
)


class GoalProductAddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Cantidad",
            "min": "1"
        }),
        label="Cantidad"
    )
