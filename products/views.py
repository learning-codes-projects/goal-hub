import base64
from io import BytesIO
from PIL import Image


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Product
from .forms import ProductForm

MIME_MAP = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "gif": "image/gif",
}


def _infer_mime_from_bytes(img_bytes: bytes) -> str:
    try:
        img = Image.open(BytesIO(img_bytes))
        fmt = (img.format or "").lower()
        return MIME_MAP.get(fmt, "application/octet-stream")
    except Exception:
        return "application/octet-stream"
    
def _parse_base64_input(value: str) -> tuple[str, str]:
    """
    Acepta:
    - data:image/png;base64,AAAA...
    - AAAA... (base64 puro)
    Retorna: (mime, b64)
    """
    value = (value or "").strip()
    if not value:
        return ("", "")

    if value.startswith("data:") and ";base64," in value:
        header, b64 = value.split(";base64,", 1)
        mime = header.replace("data:", "").strip()
        return (mime, b64.strip())

    # base64 puro -> inferimos mime desde los bytes
    img_bytes = base64.b64decode(value, validate=False)
    mime = _infer_mime_from_bytes(img_bytes)
    return (mime, value)



class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    def form_valid(self, form):
        # 1) Si suben archivo -> lo codificamos
        upload = form.cleaned_data.get("photo")
        if upload:
            b64 = base64.b64encode(upload.read()).decode("utf-8")
            form.instance.photo_b64 = b64
            form.instance.photo_mime = getattr(upload, "content_type", "") or "application/octet-stream"
            # opcional: no guardar archivo físico
            form.instance.photo = None



        return super().form_valid(form)

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"pk": self.pk})



class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    def form_valid(self, form):
        upload = form.cleaned_data.get("photo")
 

        # Solo reemplaza si llega algo nuevo; si no, mantiene lo que tenía
        if upload:
            b64 = base64.b64encode(upload.read()).decode("utf-8")
            form.instance.photo_b64 = b64
            form.instance.photo_mime = getattr(upload, "content_type", "") or "application/octet-stream"
            form.instance.photo = None

  

        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("products:list")
