from django.db import models
from django.urls import reverse


class Product(models.Model):
    # Lo dejo por compatibilidad (opcional). Podés borrarlo después si ya no lo querés.
    photo = models.ImageField("Foto", upload_to="products/", blank=True, null=True)

    # ✅ NUEVO: foto en Base64 en DB
    photo_b64 = models.TextField("Foto (Base64)", blank=True)
    photo_mime = models.CharField("Foto MIME", max_length=50, blank=True)  # image/jpeg, image/png...

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"pk": self.pk})

    @property
    def photo_src(self) -> str:
        """Devuelve src listo para <img>, prioriza Base64 y si no hay, usa ImageField."""
        if self.photo_b64 and self.photo_mime:
            return f"data:{self.photo_mime};base64,{self.photo_b64}"
        if self.photo:
            return self.photo.url
        return ""
