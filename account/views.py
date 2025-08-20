from django.conf import settings
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import User


def login_view(request):
    """
    Render the login page.
    """
    return render(request, "account/login.html")


def logout_view(request):
    """
    Render the logout page.
    """
    logout(request)
    return redirect("home")


def github_login(request):
    """We need to redirect the user to the GitHub OAuth2 authorization URL.
    To split use %20
    """
    auth = f"{settings.GITHUB_OAUTH2_AUTH_URL}?client_id={settings.GITHUB_CLIENT_ID}&scope={'%20'.join(settings.GITHUB_OAUTH2_USER_SCOPE)}"
    return redirect(auth)

def github_callback(request):
    """
    Handle the GitHub OAuth2 callback.
    """
    code = request.GET.get("code")
    if not code:
        return redirect("login")

    # Exchange the code for an access token
    token_url = settings.GITHUB_OAUTH2_TOKEN_URL
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
    }
    response = requests.post(token_url, data=data, headers={"Accept": "application/json"})
    response_data = response.json()
    access_token = response_data.get("access_token")

    if not access_token:
        return redirect("login")

    # Use the access token to get the user's information
    user_url = settings.GITHUB_OAUTH2_USER_URL
    headers = {"Authorization": f"Bearer {access_token}"}
    user_response = requests.get(user_url, headers=headers)
    user_data = user_response.json()

    # Log the user in or create a new account
    user, created = User.objects.get_or_create(
        uid=user_data["id"],
        defaults={
            "email": user_data["email"],
            "name": user_data["name"],
            "access_token": access_token
        }
    )

    if created:
        user.set_unusable_password()
    login(request, user)

    user.update_user_profile()

    return redirect("home")


@login_required
def profile_view(request):
    """
    Render the user's profile page.
    """
    return render(request, "account/profile.html")