# goals/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseForbidden

from .models import Goal
from .forms import GoalForm, GoalProductFormSet


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = "goals/index.html"
    context_object_name = "goals"

    def get_queryset(self):
        # Solo goals del usuario logueado
        return Goal.objects.filter(owner=self.request.user).order_by("-created_at")


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/add_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = GoalProductFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = GoalProductFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        form.instance.owner = self.request.user
        
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = Goal
    form_class = GoalForm
    template_name = "goals/edit_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["formset"] = GoalProductFormSet(self.request.POST, instance=self.object)
        else:
            context["formset"] = GoalProductFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    model = Goal
    template_name = "goals/delete_goals.html"
    success_url = reverse_lazy("goals:index")

    def get_queryset(self):
        return Goal.objects.filter(owner=self.request.user)
