from django.urls import path
from .views import MyProfileView

urlpatterns = [
    path("", MyProfileView.as_view(), name="my_profile"),
]
