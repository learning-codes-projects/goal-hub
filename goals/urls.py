from django.urls import path
from .views import (
    GoalListView,
    AllGoalsView,
    GoalCreateView,
    GoalUpdateView,
    GoalDeleteView,
    GoalProductsListView,
    GoalProductDetailView,
    GoalProductsByGoalView,
)

app_name = "goals"

urlpatterns = [
    path("", GoalListView.as_view(), name="index"),
    path("all/", AllGoalsView.as_view(), name="all"),
    path("create/", GoalCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", GoalUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", GoalDeleteView.as_view(), name="delete"),
    # Catálogo de productos Goals
    path("catalog/", GoalProductsListView.as_view(), name="catalog"),
    path("catalog/<int:pk>/", GoalProductDetailView.as_view(), name="product_detail"),
    # Productos de un goal específico
    path("<int:goal_id>/products/", GoalProductsByGoalView.as_view(), name="goal_products"),
]