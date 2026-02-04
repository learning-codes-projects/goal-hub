# cart/services.py
from decimal import Decimal
from django.db import transaction, IntegrityError


from products.models import Product
from .models import Cart, CartItem


class CartServiceError(Exception):
    """Error genérico de carrito (para mostrar mensajes)."""
    pass

@transaction.atomic
def get_or_create_active_cart(user) -> Cart:
    qs = (
        Cart.objects
        .select_for_update()
        .filter(user=user, status=Cart.Status.ACTIVE)
        .order_by("-updated_at", "-id")
    )

    cart = qs.first()
    if cart:
        # si por algún motivo hay 2 ACTIVE, dejamos 1 y cerramos el resto
        qs.exclude(pk=cart.pk).update(status=Cart.Status.ABANDONED)
        return cart

    return Cart.objects.create(user=user, status=Cart.Status.ACTIVE)

@transaction.atomic
def add_item(user, product_id: int, quantity: int = 1) -> Cart:
    cart = get_or_create_active_cart(user)

    try:
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        raise CartServiceError("El producto no existe o está inactivo.")

    qty = max(1, int(quantity))

    # Regla de UX: no dejar superar stock (opcional)
    if product.stock <= 0:
        raise CartServiceError("No hay stock disponible.")
    qty = min(qty, product.stock)

    try:
        item = CartItem.objects.filter(cart=cart, product=product).first()
        if item:
            new_qty = min(item.quantity + qty, product.stock)
            item.quantity = new_qty
            item.unit_price = product.price
            item.save(update_fields=["quantity", "unit_price"])
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=qty,
                unit_price=product.price,
            )
    except IntegrityError:
        # Por ejemplo: si un bug intenta crear el mismo producto 2 veces (uniq_cart_product)
        raise CartServiceError("No se pudo agregar el producto al carrito (duplicado o datos inválidos).")

    recalc_totals(cart)
    return cart



@transaction.atomic
def set_item_quantity(user, item_id: int, quantity: int) -> Cart:
    cart = get_or_create_active_cart(user)

    item = CartItem.objects.select_for_update().select_related("product").filter(
        pk=item_id, cart=cart
    ).first()
    if not item:
        raise CartServiceError("Ese ítem no existe en tu carrito activo.")

    qty = int(quantity)

    if qty <= 0:
        item.delete()
        recalc_totals(cart)
        return cart

    product = item.product
    if not product.is_active:
        raise CartServiceError("El producto está inactivo.")
    if product.stock < qty:
        raise CartServiceError(f"Stock insuficiente. Disponible: {product.stock}.")

    item.quantity = qty
    item.unit_price = product.price
    item.save(update_fields=["quantity", "unit_price"])

    recalc_totals(cart)
    return cart



def remove_item(user, product_id: int) -> Cart:
    cart = get_or_create_active_cart(user)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    recalc_totals(cart)
    return cart


def recalc_totals(cart: Cart) -> None:
    subtotal = Decimal("0.00")
    for item in cart.items.all():
        subtotal += item.unit_price * item.quantity

    cart.subtotal = subtotal
    cart.total = subtotal
    cart.save(update_fields=["subtotal", "total", "updated_at"])
