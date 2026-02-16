# cart/services.py
from decimal import Decimal
from django.db import transaction, IntegrityError
from django.utils import timezone

from products.models import Product
from goals.models import GoalProduct, Goal
from .models import Cart, CartItem, Order, OrderItem



class CartServiceError(Exception):
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
def add_item(user, product_id: int, quantity: int = 1, goal_id: int = None) -> Cart:
    cart = get_or_create_active_cart(user)

    try:
        product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
    except Product.DoesNotExist:
        raise CartServiceError("El producto no existe o está inactivo.")

    qty = max(1, int(quantity))
    goal_obj = None

    # Validar stock disponible
    if goal_id:
        # Validar contra el Goal ESPECÍFICO
        try:
            goal_obj = Goal.objects.select_for_update().get(
                pk=goal_id,
                status=Goal.Status.ACTIVE
            )
            goal_product = GoalProduct.objects.select_for_update().get(
                product_id=product_id,
                goal_id=goal_id
            )
        except (Goal.DoesNotExist, GoalProduct.DoesNotExist):
            raise CartServiceError("Ese producto no está disponible en ese objetivo.")
        
        available = goal_product.goal_stock_available
        
        if available <= 0:
            raise CartServiceError(
                f"No hay stock disponible en el objetivo '{goal_obj.title}'."
            )
        
        qty = min(qty, available)
    else:
        # Validar contra stock global del producto
        if product.stock <= 0:
            raise CartServiceError("No hay stock disponible.")
        qty = min(qty, product.stock)

    try:
        item = CartItem.objects.filter(cart=cart, product=product, goal=goal_obj).first()
        if item:
            new_qty = item.quantity + qty
            
            # Re-validar stock con la nueva cantidad
            if goal_id:
                goal_product = GoalProduct.objects.get(product_id=product_id, goal_id=goal_id)
                available = goal_product.goal_stock_available
                new_qty = min(new_qty, item.quantity + available)
            else:
                new_qty = min(new_qty, product.stock)
            
            item.quantity = new_qty
            item.unit_price = product.price
            item.save(update_fields=["quantity", "unit_price"])
        else:
            CartItem.objects.create(
                cart=cart,
                product=product,
                goal=goal_obj,
                quantity=qty,
                unit_price=product.price,
            )
    except IntegrityError:
        raise CartServiceError("Error al agregar el producto al carrito.")

    recalc_totals(cart)
    return cart



@transaction.atomic
def set_item_quantity(user, item_id: int, quantity: int) -> Cart:
    cart = get_or_create_active_cart(user)

    item = CartItem.objects.select_for_update().select_related("product", "goal").filter(
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
    
    # Validar stock según si vino de un goal o no
    if item.goal:
        goal_product = GoalProduct.objects.select_for_update().get(
            product_id=product.id,
            goal_id=item.goal.id
        )
        available = goal_product.goal_stock_available
        if available < qty:
            raise CartServiceError(
                f"Stock insuficiente. Disponible en objetivo: {available}."
            )
    else:
        if product.stock < qty:
            raise CartServiceError(f"Stock insuficiente. Disponible: {product.stock}.")

    item.quantity = qty
    item.unit_price = product.price
    item.save(update_fields=["quantity", "unit_price"])

    recalc_totals(cart)
    return cart



def remove_item(user, item_id: int) -> Cart:
    cart = get_or_create_active_cart(user)
    CartItem.objects.filter(pk=item_id, cart=cart).delete()
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
    # Obtener carrito lockeado
    cart = (
        Cart.objects
        .select_for_update()
        .filter(user=user, status=Cart.Status.ACTIVE)
        .first()
    )
    
    if not cart:
        raise CartServiceError("No tienes un carrito activo.")

    # Leer todos los items del carrito
    cart_items = list(cart.items.select_related("product", "goal").all())
    
    if not cart_items:
        raise CartServiceError("El carrito está vacío.")

    # Extraer product_ids únicos y lockear todos los productos
    product_ids = [item.product_id for item in cart_items]
    products_by_id = {}
    
    for product in Product.objects.select_for_update().filter(id__in=product_ids):
        products_by_id[product.id] = product

    # Validar que todos los productos existen
    if len(products_by_id) != len(set(product_ids)):
        raise CartServiceError("Uno o más productos no existen.")

    # ✅ FASE 1: Validar stock disponible
    for cart_item in cart_items:
        product = products_by_id[cart_item.product_id]
        quantity = cart_item.quantity

        if not product.is_active:
            raise CartServiceError(f"El producto '{product.name}' está inactivo.")

        if product.stock < quantity:
            raise CartServiceError(
                f"Stock insuficiente para '{product.name}'. "
                f"Disponible: {product.stock}, solicitado: {quantity}."
            )

        # Si viene de un Goal, validar también ese stock
        if cart_item.goal:
            try:
                goal_product = GoalProduct.objects.select_for_update().get(
                    product=product,
                    goal=cart_item.goal
                )
                if goal_product.goal_stock_available < quantity:
                    raise CartServiceError(
                        f"Stock insuficiente para '{product.name}' en el objetivo "
                        f"'{cart_item.goal.title}'. Disponible: {goal_product.goal_stock_available}."
                    )
            except GoalProduct.DoesNotExist:
                raise CartServiceError(
                    f"El producto '{product.name}' no está disponible en ese objetivo."
                )

    # ✅ FASE 2: Crear Order
    order = Order.objects.create(
        user=user,
        cart=cart,
        subtotal=cart.subtotal,
        total=cart.total,
        status=Order.Status.COMPLETED
    )

    # ✅ FASE 3: Procesar items, crear OrderItems y agrupar decrementos
    product_stock_decrement = {}  # Agrupar decrementos por producto
    goal_product_decrement = {}   # Agrupar decrementos por GoalProduct

    for cart_item in cart_items:
        product = products_by_id[cart_item.product_id]
        quantity = cart_item.quantity
        unit_price = cart_item.unit_price
        goal = cart_item.goal

        # Crear OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            goal=goal,
            quantity=quantity,
            unit_price=unit_price
        )

        # Acumular decrementos de GoalProduct por clave única
        if goal:
            key = (product.id, goal.id)
            goal_product_decrement[key] = goal_product_decrement.get(key, 0) + quantity

        # Registrar decremento de stock global del producto
        product_stock_decrement[product.id] = product_stock_decrement.get(product.id, 0) + quantity

    # ✅ FASE 4a: Calcular incrementos totales POR GOAL (agrupar múltiples productos)
    goal_increments = {}  # {goal_id: total_decimal_amount}
    for (product_id, goal_id), total_qty in goal_product_decrement.items():
        goal_product = GoalProduct.objects.select_for_update().get(
            product_id=product_id,
            goal_id=goal_id
        )
        amount_to_add = Decimal(str(total_qty)) * Decimal(str(goal_product.unit_price))
        
        if goal_id not in goal_increments:
            goal_increments[goal_id] = Decimal("0.00")
        goal_increments[goal_id] += amount_to_add

    # ✅ FASE 4b: Actualizar CADA GOAL UNA SOLA VEZ con el total acumulado
    for goal_id, total_increment in goal_increments.items():
        goal = Goal.objects.select_for_update().get(pk=goal_id)
        goal.amount_raised += total_increment
        goal.save(update_fields=["amount_raised", "updated_at"])
        goal.evaluate_completion()

    # ✅ FASE 4c: Actualizar GoalProduct.goal_stock_sold
    for (product_id, goal_id), total_qty in goal_product_decrement.items():
        goal_product = GoalProduct.objects.select_for_update().get(
            product_id=product_id,
            goal_id=goal_id
        )
        goal_product.goal_stock_sold += total_qty
        goal_product.save(update_fields=["goal_stock_sold"])

    # ✅ FASE 4b: Decrementar stock de productos (acumulativamente)
    for product_id, total_qty in product_stock_decrement.items():
        product = products_by_id[product_id]
        product.stock -= total_qty
        product.save(update_fields=["stock"])

    # ✅ FASE 5: Marcar carrito como completado
    cart.status = Cart.Status.CHECKED_OUT
    cart.checked_out_at = timezone.now()
    cart.save(update_fields=["status", "checked_out_at"])

    return order