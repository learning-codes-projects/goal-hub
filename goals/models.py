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
        """
        Evalúa el estado del goal según:
        - monto alcanzado
        - stock asignado al goal agotado
        """
        if self.status in {self.Status.CANCELED, self.Status.ACHIEVED, self.Status.EXHAUSTED}:
            return

        amount_ok = self.target_amount > 0 and self.amount_raised >= self.target_amount
        out_of_stock = not self.items.filter(goal_stock__gt=0).exists()

        if self.complete_when == self.CompleteWhen.AMOUNT and amount_ok:
            self.status = self.Status.ACHIEVED

        elif self.complete_when == self.CompleteWhen.STOCK and out_of_stock:
            self.status = self.Status.EXHAUSTED

        elif self.complete_when == self.CompleteWhen.EITHER and (amount_ok or out_of_stock):
            self.status = self.Status.ACHIEVED if amount_ok else self.Status.EXHAUSTED

    @property
    def goal_stock_total(self) -> int:
        """Stock total asignado a este goal (suma de todos los GoalProduct.goal_stock)."""
        return int(self.items.aggregate(total=models.Sum("goal_stock"))["total"] or 0)

    @property
    def potential_amount(self):
        """
        Monto potencial si se consume todo el stock del goal:
        SUM(goal_stock * unit_price)
        """
        # Nota: ExpressionWrapper para calcular en DB sin iterar en Python.
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
