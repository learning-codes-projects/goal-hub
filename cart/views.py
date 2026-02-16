# cart/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, DetailView


from .forms import CartItemCreateForm, CartItemUpdateForm
from .models import Order, OrderItem

from .services import (
    CartServiceError,
    add_item,
    get_or_create_active_cart,
    remove_item,
    set_item_quantity,
    checkout,
)


@login_required
def cart_detail(request):
    cart = get_or_create_active_cart(request.user)
    items = cart.items.select_related("product").all()
    return render(request, "cart/cart_detail.html", {"cart": cart, "items": items})

@require_http_methods(["GET", "POST"])
@login_required
def cart_item_create(request):
    if request.method == "POST":
        form = CartItemCreateForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]
            try:
                add_item(request.user, product_id=product.id, quantity=quantity)
                messages.success(request, "Ítem agregado al carrito.")
                return redirect("cart:detail")
            except CartServiceError as e:
                messages.error(request, str(e))
    else:
        form = CartItemCreateForm()

    return render(request, "cart/item_form.html", {"form": form, "title": "Agregar ítem"})

@require_http_methods(["GET", "POST"])
@login_required
def cart_item_update(request, item_id: int):
    cart = get_or_create_active_cart(request.user)
    item = cart.items.select_related("product").filter(pk=item_id).first()
    if not item:
        messages.error(request, "Ese ítem no existe en tu carrito.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CartItemUpdateForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            try:
                set_item_quantity(request.user, item_id=item_id, quantity=quantity)
                messages.success(request, "Ítem actualizado.")
                return redirect("cart:detail")
            except CartServiceError as e:
                messages.error(request, str(e))
    else:
        form = CartItemUpdateForm(initial={"quantity": item.quantity})

    return render(
        request,
        "cart/item_form.html",
        {"form": form, "title": f"Editar {item.product.name}", "item": item},
    )

@require_POST
@login_required
def cart_item_delete(request,  item_id: int):
    try:
        remove_item(request.user,  item_id= item_id)
        messages.info(request, "Ítem eliminado del carrito.")
    except CartServiceError as e:
        messages.error(request, str(e))

    return redirect("cart:detail")

@require_POST
@login_required
def cart_add(request, product_id: int):
    qty = request.POST.get("quantity", 1)

    try:
        add_item(user=request.user, product_id=product_id, quantity=qty)
        messages.success(request, "Producto agregado al carrito.")
    except CartServiceError as e:
        messages.error(request, str(e))

    return redirect("cart:detail")




@require_POST
@login_required
def cart_remove(request, product_id: int):
    remove_item(request.user, product_id=product_id)
    messages.info(request, "Producto eliminado del carrito.")
    return redirect("cart:detail")

@require_POST
@login_required
def cart_checkout(request):

    try:
        order = checkout(request.user)
        messages.success(request, f"✓ Pedido realizado exitosamente. Pedido #{order.id}")
        return redirect("cart:order_list")
    except CartServiceError as e:
        messages.error(request, str(e))
        return redirect("cart:detail")
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        messages.error(request, f"Error inesperado: {str(e)}")
        return redirect("cart:detail")


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "cart/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "items__goal")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "cart/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "items__goal")