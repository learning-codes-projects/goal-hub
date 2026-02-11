# goals/forms.py
from django import forms
from django.forms import inlineformset_factory
import base64

from products.models import Product
from .models import Goal, GoalProduct


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
        fields = ["title", "target_amount", "complete_when"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del objetivo"
            }),
            "target_amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Monto objetivo",
                "step": "0.01",
                "min": "0"
            }),
            "complete_when": forms.Select(attrs={
                "class": "form-select"
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
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Producto"
    )

    class Meta:
        model = GoalProduct
        fields = ["product", "goal_stock", "unit_price"]
        widgets = {
            "goal_stock": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Stock del objetivo",
                "min": "0"
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Precio unitario",
                "step": "0.01",
                "min": "0"
            }),
        }


GoalProductFormSet = inlineformset_factory(
    Goal,
    GoalProduct,
    form=GoalProductForm,
    extra=1,
    can_delete=True
)
