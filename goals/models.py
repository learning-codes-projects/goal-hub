# goals/models.py
from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Goal(models.Model):
    """
    Objetivo/Campaña del owner.

    Se puede marcar como:
    - ACHIEVED: si se alcanzó el monto (amount_raised >= target_amount)
    - EXHAUSTED: si se agotó el stock asignado al goal (GoalProduct.goal_stock == 0 en todos)
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Activo"
        ACHIEVED = "achieved", "Cumplido (monto)"
        EXHAUSTED = "exhausted", "Finalizado (sin stock)"
        CANCELED = "canceled", "Cancelado"

    class CompleteWhen(models.TextChoices):
        AMOUNT = "amount", "Solo por monto"
        STOCK = "stock", "Solo por stock (sin stock)"
        EITHER = "either", "Monto o sin stock"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
    )

    title = models.CharField(max_length=120)
    
    # Lo dejo por compatibilidad (opcional). Podés borrarlo después si ya no lo querés.
    photo = models.ImageField(
        "Foto",
        upload_to="goals/",
        blank=True,
        null=True
    )

    # ✅ NUEVO: foto en Base64 en DB
    photo_b64 = models.TextField("Foto (Base64)", blank=True)
    photo_mime = models.CharField("Foto MIME", max_length=50, blank=True)  # image/jpeg, image/png...

    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    amount_raised = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    complete_when = models.CharField(
        max_length=10,
        choices=CompleteWhen.choices,
        default=CompleteWhen.AMOUNT,
        db_index=True,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )

    achieved_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["status", "complete_when"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def evaluate_completion(self) -> None:
        if self.status in {self.Status.CANCELED, self.Status.ACHIEVED, self.Status.EXHAUSTED}:
            return

        # Verificar si se alcanzó el monto objetivo (calculado desde los productos asignados)
        target_total = self.computed_target_amount
        amount_ok = target_total > 0 and self.amount_raised >= target_total

        # ✅ Verificar si se agotó el stock (stock disponible = 0)
        current_stock = self.goal_stock_total
        out_of_stock = current_stock == 0 and int(
            self.items.aggregate(total=models.Sum("goal_stock"))["total"] or 0
        ) > 0

        # Definir estado basado en complete_when
        new_status = None
        
        if self.complete_when == self.CompleteWhen.AMOUNT:
            if amount_ok:
                new_status = self.Status.ACHIEVED
        elif self.complete_when == self.CompleteWhen.STOCK:
            if out_of_stock:
                new_status = self.Status.EXHAUSTED
        elif self.complete_when == self.CompleteWhen.EITHER:
            if amount_ok:
                new_status = self.Status.ACHIEVED
            elif out_of_stock:
                new_status = self.Status.EXHAUSTED

        # Guardar cambios si hay un cambio de estado
        if new_status and new_status != self.status:
            from django.utils import timezone
            self.status = new_status
            self.achieved_at = timezone.now()
            self.save(update_fields=["status", "achieved_at", "updated_at"])

    @property
    def goal_stock_total(self) -> int:
        """
        Stock DISPONIBLE (sin vender) del goal.
        = SUM(goal_stock - goal_stock_sold) de todos los GoalProducts
        """
        from django.db.models import ExpressionWrapper, IntegerField
        expr = ExpressionWrapper(
            models.F("goal_stock") - models.F("goal_stock_sold"),
            output_field=IntegerField(),
        )
        return int(
            self.items.aggregate(total=models.Sum(expr))["total"] or 0
        )


    @property
    def computed_target_amount(self):
        """
        Monto objetivo calculado a partir de los productos asignados al goal:
        SUM(goal_stock * unit_price)
        """
        expr = models.ExpressionWrapper(
            models.F("goal_stock") * models.F("unit_price"),
            output_field=models.DecimalField(max_digits=14, decimal_places=2),
        )
        return self.items.aggregate(total=models.Sum(expr))["total"] or 0

    @property
    def photo_src(self) -> str:
        """Devuelve src listo para <img>, prioriza Base64 y si no hay, usa ImageField."""
        if self.photo_b64 and self.photo_mime:
            return f"data:{self.photo_mime};base64,{self.photo_b64}"
        if self.photo:
            return self.photo.url
        return ""
    
    def get_status_display_verbose(self) -> str:
        """
        Devuelve descripción verbal del estado del goal.
        """
        status_labels = {
            self.Status.ACTIVE: "Activo - Sin completar",
            self.Status.ACHIEVED: "Completado ✓ (Monto alcanzado)",
            self.Status.EXHAUSTED: "Finalizado (Sin stock)",
            self.Status.CANCELED: "Cancelado",
        }
        return status_labels.get(self.status, self.get_status_display())
    
    def get_completion_progress(self) -> dict:
        """
        Retorna un diccionario con el progreso de cumplimiento del goal:
        - amount_raised: monto ya recaudado
        - target_amount: monto objetivo calculado desde los productos
        - goal_stock_total: cantidad total de items sin vender
        - percentage: porcentaje de completitud (0-100)
        - is_complete: booleano si está completado
        - status_verbose: descripción del estado
        """
        target = self.computed_target_amount
        stock = self.goal_stock_total

        percentage = 0
        if target > 0:
            percentage = min(100, int((float(self.amount_raised) / float(target)) * 100))

        return {
            "amount_raised": self.amount_raised,
            "target_amount": target,
            "goal_stock_total": stock,
            "percentage": percentage,
            "is_complete": self.status in {self.Status.ACHIEVED, self.Status.EXHAUSTED},
            "status_verbose": self.get_status_display_verbose(),
        }


class GoalProduct(models.Model):
    """
    Item / línea de producto dentro del Goal.
    Guarda el 'stock del goal' (reservado para esa campaña) + un precio snapshot.
    """

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="goal_items",
    )

    goal_stock = models.PositiveIntegerField(default=0)
    # ✅ NUEVO: Track cuánto se ha vendido en este objetivo
    goal_stock_sold = models.PositiveIntegerField(default=0)

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    position = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "id"]
        constraints = [
            models.UniqueConstraint(fields=["goal", "product"], name="uniq_goal_product"),
        ]

    def __str__(self) -> str:
        return f"{self.goal_id} - {self.product_id} ({self.goal_stock})"

    @property
    def goal_stock_available(self) -> int:
        """Stock disponible para vender (inicial - vendido)."""
        return max(0, self.goal_stock - self.goal_stock_sold)
