from django.db import models
from django.contrib.auth.models import AbstractUser
import requests
from django.conf import settings

SCOPE = ["user:email", "read:user"]


class User(AbstractUser):
    """
    Custom user model for GitHub OAuth2 authentication.
    """

    uid = models.CharField(max_length=255, help_text="GitHub user ID", unique=True, null=True, blank=True)
    access_token = models.CharField(
        max_length=255, blank=True, null=True, help_text="GitHub OAuth2 access token"
    )
    name = models.CharField(
        max_length=255, blank=True, null=True, help_text="GitHub user name"
    )
    avatar_url = models.URLField(
        max_length=255, blank=True, null=True, help_text="GitHub user avatar URL"
    )
    bio = models.TextField(blank=True, null=True, help_text="GitHub user bio")

    raw_data = models.JSONField(
        blank=True, null=True, help_text="Raw data from GitHub API"
    )

    def __str__(self):
        return self.name or self.username
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]

    def fetch_github_data(self):
        """
        Fetch the user's GitHub data.
        """
        if not self.access_token:
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(settings.GITHUB_OAUTH2_USER_URL, headers=headers)
        return response.json()

    def fetch_github_emails(self):
        """
        Fetch the user's GitHub email addresses.
        """
        if not self.access_token:
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(settings.GITHUB_OAUTH2_EMAILS_URL, headers=headers)
        return response.json()

    def update_user_profile(self):
        """
        Update the user's profile information.
        """
        github_data = self.fetch_github_data()
        if not github_data:
            return

        self.raw_data = github_data
        self.name = github_data.get("name", self.name)
        self.uid = str(github_data.get("id", self.uid))
        self.access_token = github_data.get("access_token", self.access_token)
        self.username = github_data.get("login", self.username)
        self.avatar_url = github_data.get("avatar_url", self.avatar_url)
        self.bio = github_data.get("bio", self.bio)
        self.save()

        emails = self.fetch_github_emails()
        if emails:
            for email in emails:
                if email.get("primary") and email.get("email") and email.get("visibility") == "public":
                    self.email = email.get("email")
                    self.save()
