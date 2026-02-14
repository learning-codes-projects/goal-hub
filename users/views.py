from django.views.generic import TemplateView


class UsersView(TemplateView):
    """Vista del dashboard principal."""

    template_name = "users/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Users"
        return context
