# accounts/views.py
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse

def login_view(request):
    # Si ya está logueado, lo mandamos al dashboard
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)  # <-- FORM REAL
        if form.is_valid():
            user = form.get_user()
            dj_login(request, user)
            # soporte de next (si venís de una ruta protegida)
            next_url = request.GET.get("next") or reverse("dashboard")
            return redirect(next_url)
    else:
        form = AuthenticationForm(request)  # <-- FORM VACÍO

    return render(request, "login/index.html", {"form": form})

def logout_view(request):
    dj_logout(request)
    return redirect("login")

@login_required
def dashboard_view(request):
    return render(request, "dashboard/index.html", {"title": "Dashboard"})
