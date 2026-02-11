from django.contrib import admin

from .models import Goal, GoalProduct


class GoalProductInline(admin.TabularInline):
    model = GoalProduct
    extra = 1
    fields = ("product", "goal_stock", "unit_price", "position")
    ordering = ("position", "id")


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "target_amount", "amount_raised", "created_at")
    list_filter = ("status", "complete_when", "created_at")
    search_fields = ("title", "owner__username")
    readonly_fields = ("amount_raised", "achieved_at", "ended_at", "created_at", "updated_at", "photo_preview")
    inlines = [GoalProductInline]
    
    fieldsets = (
        ("Información General", {
            "fields": ("title", "owner")
        }),
        ("Foto", {
            "fields": ("photo", "photo_b64", "photo_mime", "photo_preview"),
            "classes": ("collapse",)
        }),
        ("Objetivo Financiero", {
            "fields": ("target_amount", "complete_when")
        }),
        ("Estado", {
            "fields": ("status", "amount_raised", "achieved_at", "ended_at")
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo_src:
            return f'<img src="{obj.photo_src}" style="max-width: 200px; max-height: 200px;">'
        return "Sin foto"
    photo_preview.allow_tags = True
    photo_preview.short_description = "Vista previa"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(owner=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(GoalProduct)
class GoalProductAdmin(admin.ModelAdmin):
    list_display = ("id", "goal", "product", "goal_stock", "unit_price", "position")
    list_filter = ("goal", "created_at")
    search_fields = ("goal__title", "product__name")
    ordering = ("goal", "position", "id")
