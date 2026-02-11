from django.urls import path
from .views import GoalListView, GoalCreateView, GoalUpdateView, GoalDeleteView

app_name = "goals"

urlpatterns = [
    path("", GoalListView.as_view(), name="index"),
    path("create/", GoalCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", GoalUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", GoalDeleteView.as_view(), name="delete"),
]