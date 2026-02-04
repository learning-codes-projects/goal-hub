# cart/urls.py
from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.cart_detail, name="detail"),
    path("add/<int:product_id>/", views.cart_add, name="add"),
    path("remove/<int:product_id>/", views.cart_remove, name="remove"),

    path("items/new/", views.cart_item_create, name="item_create"),
    path("items/<int:item_id>/edit/", views.cart_item_update, name="item_update"),
    path("items/<int:item_id>/delete/", views.cart_item_delete, name="item_delete"),
]
