import base64
from io import BytesIO
from PIL import Image


from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

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



class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    permission_required = "products.view_product"
    raise_exception = True

class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    permission_required = "products.view_product"
    raise_exception = True


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    permission_required = "products.add_product"
    raise_exception = True  # <- logueado sin permiso => 403

    def form_valid(self, form):
        upload = form.cleaned_data.get("photo")
        if upload:
            b64 = base64.b64encode(upload.read()).decode("utf-8")
            form.instance.photo_b64 = b64
            form.instance.photo_mime = getattr(upload, "content_type", "") or "application/octet-stream"
            form.instance.photo = None
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("products:detail", kwargs={"pk": self.object.pk})


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"

    permission_required = "products.change_product"
    raise_exception = True

    def form_valid(self, form):
        upload = form.cleaned_data.get("photo")
        if upload:
            b64 = base64.b64encode(upload.read()).decode("utf-8")
            form.instance.photo_b64 = b64
            form.instance.photo_mime = getattr(upload, "content_type", "") or "application/octet-stream"
            form.instance.photo = None
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("products:detail", kwargs={"pk": self.object.pk})


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("products:list")

    permission_required = "products.delete_product"
    raise_exception = True

@require_POST
@login_required
def cart_add(request, product_id: int):
    qty = request.POST.get("quantity", 1)

    try:
        add_item(request.user, product_id=product_id, quantity=qty)
        messages.success(request, "Producto agregado al carrito.")
    except CartServiceError as e:
        messages.error(request, str(e))

    return redirect("cart:detail")
