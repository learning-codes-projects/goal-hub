

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("dashboard.urls")),
    path("users/", include("users.urls")),
    path("register/", include("register.urls")),
    path("", include("login.urls")),
    path("my_profile/", include("my_profile.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("goals/", include("goals.urls")),
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
