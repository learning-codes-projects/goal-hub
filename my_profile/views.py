from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = "my_profile/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Mi perfil"
        return ctx
