# accounts/views.py
import logging
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

logger = logging.getLogger(__name__)


class RegisterView(FormView):
    template_name = "register/index.html"
    form_class = UserCreationForm
    success_url = reverse_lazy(
        "dashboard:index"
    )  # Redirige al formulario de registro después de guardar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Register"
        return context

    def form_valid(self, form):
        try:
            logger.info(f"Formulario válido. Datos: {form.cleaned_data}")
            with transaction.atomic():
                user = form.save()
                logger.info(f"Usuario guardado: {user.username}, ID: {user.id}")
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error al guardar usuario: {str(e)}", exc_info=True)
            raise

    def form_invalid(self, form):
        logger.warning(f"Formulario inválido. Errores: {form.errors}")
        return super().form_invalid(form)
