# accounts/views.py
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            dj_login(request, form.get_user())

            next_url = request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)

            return redirect("dashboard:home")
    else:
        form = AuthenticationForm(request)

    return render(request, "login/index.html", {"form": form})

def logout_view(request):
    dj_logout(request)
    return redirect("login")


