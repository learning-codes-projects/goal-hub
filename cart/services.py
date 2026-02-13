# cart/services.py
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.utils import timezone

from products.models import Product
from goals.models import GoalProduct, Goal
from .models import Cart, CartItem, Order, OrderItem



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

@transaction.atomic
def checkout(user) -> Order:
    """
    Procesa el checkout del carrito activo:
    1. Crea una Order con sus OrderItems
    2. Actualiza amount_raised en los Goals relacionados
    3. Evalúa si los Goals se completaron
    4. Marca el carrito como CHECKED_OUT
    5. Decrementa el stock de los productos
    """
    cart = get_or_create_active_cart(user)

    if not cart.items.exists():
        raise CartServiceError("El carrito está vacío.")

    # Crear la Order
    order = Order.objects.create(
        user=user,
        cart=cart,
        subtotal=cart.subtotal,
        total=cart.total,
        status=Order.Status.COMPLETED
    )

    # Procesar cada ítem del carrito
    for cart_item in cart.items.select_related("product").all():
        product = cart_item.product
        quantity = cart_item.quantity
        unit_price = cart_item.unit_price

        # Buscar si este producto vino de un GoalProduct
        goal_related = None
        goal_product = None
        goal_products = GoalProduct.objects.select_for_update().filter(product=product).select_related("goal")
        
        if goal_products.exists():
            # Si hay multiple GoalProducts del mismo producto, usar el primero
            goal_product = goal_products.first()
            goal_related = goal_product.goal

        # Crear OrderItem
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            goal=goal_related,
            quantity=quantity,
            unit_price=unit_price
        )

        # Actualizar amount_raised en el Goal si existe.
        # Nota: no decrementamos `GoalProduct.goal_stock` aquí para preservar
        # el "monto potencial" y el "monto objetivo" calculados a partir
        # del stock inicial asignado al goal. Esto evita que esos valores
        # disminuyan cuando se concreta una compra.
        if goal_related and goal_product:
            amount_to_add = Decimal(str(quantity)) * unit_price
            goal_related.amount_raised += amount_to_add
            goal_related.save(update_fields=["amount_raised", "updated_at"])

            # Evaluar si el goal se completó (por monto).
            # No evaluamos EXHAUSTED por falta de stock aquí porque
            # `goal_stock` permanece como el stock original asignado al goal.
            goal_related.evaluate_completion()

        # Decrementar stock del producto
        product.stock -= quantity
        product.save(update_fields=["stock"])

    # Marcar carrito como CHECKED_OUT
    cart.status = Cart.Status.CHECKED_OUT
    cart.checked_out_at = timezone.now()
    cart.save(update_fields=["status", "checked_out_at"])

    return order