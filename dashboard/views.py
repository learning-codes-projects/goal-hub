from django.views.generic import TemplateView


class DashboardView(TemplateView):
    """Vista del dashboard principal."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Dashboard"
        return context
