# goals/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import Goal, GoalProduct
from .forms import GoalForm, GoalProductFormSet, GoalProductAddToCartForm

class RecipientRequiredMixin:
    """Mixin que permite acceso solo a usuarios del grupo 'destinatarios' (o superusers)."""
    required_group = "destinatarios"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if request.user.is_authenticated and request.user.groups.filter(name=self.required_group).exists():
            return super().dispatch(request, *args, **kwargs)

        raise PermissionDenied

class GoalListView(LoginRequiredMixin, RecipientRequiredMixin, ListView):
    model = Goal
    template_name = "goals/index.html"
    context_object_name = "goals"

    def get_queryset(self):
        # Solo goals del usuario logueado
        return Goal.objects.filter(owner=self.request.user).order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información de progreso a cada goal
        for goal in context["goals"]:
            goal.progress = goal.get_completion_progress()
        return context

class AllGoalsView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = "goals/all_goals.html"
    context_object_name = "goals"
    paginate_by = 12

    def get_queryset(self):
        # Todos los objetivos activos, ordenados por fecha de creación
        return Goal.objects.filter(status=Goal.Status.ACTIVE).order_by("-created_at")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar información de progreso a cada goal
        for goal in context["goals"]:
            goal.progress = goal.get_completion_progress()
        return context


class GoalProductsListView(LoginRequiredMixin, ListView):
    """
    Catálogo de productos disponibles en Goals.
    Solo muestra GoalProducts con stock disponible > 0 y goal activo.
    """
    model = GoalProduct
    template_name = "goals/goal_products_list.html"
    context_object_name = "goal_products"
    paginate_by = 12

    def get_queryset(self):
        # ✅ Se filtra por goal_stock__gt=0 pero se mostrará goal_stock_available en templates
        return GoalProduct.objects.filter(
            goal__status=Goal.Status.ACTIVE
        ).select_related("goal", "product").order_by("-goal__created_at", "position")


class GoalProductDetailView(LoginRequiredMixin, DetailView):
    """
    Detalle de un producto Goal con opción de agregar al carrito.
    """
    model = GoalProduct
    template_name = "goals/goal_product_detail.html"
    context_object_name = "goal_product"

    def get_queryset(self):
        return GoalProduct.objects.filter(
            goal__status=Goal.Status.ACTIVE
        ).select_related("goal", "product")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = GoalProductAddToCartForm()
        # ✅ Usar goal_stock_available en lugar de goal_stock
        context["max_quantity"] = self.object.goal_stock_available
        context["goal_progress"] = self.object.goal.get_completion_progress()
        return context

    def post(self, request, *args, **kwargs):
        """Manejar agregar al carrito."""
        self.object = self.get_object()
        form = GoalProductAddToCartForm(request.POST)
        
        if form.is_valid():
            quantity = form.cleaned_data["quantity"]
            
            # ✅ Validar contra stock DISPONIBLE
            if quantity > self.object.goal_stock_available:
                messages.error(
                    request,
                    f"❌ Stock insuficiente. Disponible: {self.object.goal_stock_available} unidades. "
                    f"Tu cantidad: {quantity}."
                )
                context = self.get_context_data(object=self.object)
                context["form"] = form
                return self.render_to_response(context)
            
            # ✅ Validar que haya al menos 1 unidad disponible
            if self.object.goal_stock_available <= 0:
                messages.error(
                    request,
                    f"❌ No hay stock disponible para {self.object.product.name}"
                )
                context = self.get_context_data(object=self.object)
                context["form"] = form
                return self.render_to_response(context)
            
            # Agregar al carrito usando el servicio del cart
            from cart.services import add_item, CartServiceError
            
            try:
                add_item(
                    request.user, 
                    product_id=self.object.product.id, 
                    quantity=quantity,
                    goal_id=self.object.goal.id  # ✅ Pasar el goal_id
                )
                
                messages.success(
                    request,
                    f"✓ {self.object.product.name} agregado al carrito ({quantity} unidades)"
                )
                return redirect("cart:detail")
            except CartServiceError as e:
                messages.error(request, str(e))
                context = self.get_context_data(object=self.object)
                context["form"] = form
                return self.render_to_response(context)
        else:
            messages.error(request, "❌ Por favor verifica los datos ingresados")
        
        context = self.get_context_data(object=self.object)
        context["form"] = form
        return self.render_to_response(context)


class GoalProductsByGoalView(LoginRequiredMixin, ListView):
    """
    Muestra todos los productos de un goal específico.
    """
    model = GoalProduct
    template_name = "goals/goal_products_by_goal.html"
    context_object_name = "goal_products"
    paginate_by = 12

    def get_queryset(self):
        goal_id = self.kwargs.get("goal_id")
        return GoalProduct.objects.filter(
            goal_id=goal_id,
            goal__status=Goal.Status.ACTIVE
        ).select_related("goal", "product").order_by("position")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        goal_id = self.kwargs.get("goal_id")
        goal = Goal.objects.get(id=goal_id, status=Goal.Status.ACTIVE)
        context["goal"] = goal
        context["goal_progress"] = goal.get_completion_progress()
        return context


class GoalCreateView(LoginRequiredMixin, RecipientRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/add_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Permite reusar el formset con errores (si viene por kwargs)
        if "formset" in kwargs:
            context["formset"] = kwargs["formset"]
        else:
            if self.request.POST:
                context["formset"] = GoalProductFormSet(self.request.POST, instance=self.object)
            else:
                context["formset"] = GoalProductFormSet(instance=self.object)

        return context

    @transaction.atomic
    def form_valid(self, form):
        # Guardado del Goal (sin commit para setear owner)
        self.object = form.save(commit=False)
        self.object.owner = self.request.user

        # Creamos/validamos formset con el goal aún no guardado (validar ok)
        formset = GoalProductFormSet(self.request.POST, instance=self.object)

        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

        # Guardamos goal y luego el formset
        self.object.save()
        formset.instance = self.object
        formset.save()

        # Evaluar si el goal está completo basado en lo que hubiese sido asignado
        self.object.evaluate_completion()

        #messages.success(self.request, "Objetivo creado.")
        return redirect("goals:index")  # <-- redirige al index


class GoalUpdateView(LoginRequiredMixin, RecipientRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/edit_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "formset" in kwargs:
            context["formset"] = kwargs["formset"]
        else:
            if self.request.POST:
                context["formset"] = GoalProductFormSet(self.request.POST, instance=self.object)
            else:
                context["formset"] = GoalProductFormSet(instance=self.object)

        return context

    @transaction.atomic
    def form_valid(self, form):
        formset = GoalProductFormSet(self.request.POST, instance=self.object)

        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

        self.object = form.save()
        formset.instance = self.object
        formset.save()

        # Evaluar si el goal está completo basado en los cambios
        self.object.evaluate_completion()

        #messages.success(self.request, "Objetivo actualizado.")
        return redirect("goals:index")  # <-- redirige al index

class GoalDeleteView(LoginRequiredMixin, RecipientRequiredMixin, DeleteView):
    model = Goal
    template_name = "goals/delete_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)
