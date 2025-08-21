from django.core.cache import cache
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

    def fetch_github_data(self, force_refresh=False):
        """
        Fetch the user's GitHub data with caching.
        """
        if not self.access_token:
            return None

        cache_key = f"github_data:{self.pk}"
        data = cache.get(cache_key)

        if data is None or force_refresh:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(settings.GITHUB_OAUTH2_USER_URL, headers=headers)
            if response.status_code == 200:
                data = response.json()
                cache.set(cache_key, data, timeout=60 * 15)  # cache for 15 minutes
        return data

    def fetch_github_emails(self, force_refresh=False):
        """
        Fetch the user's GitHub email addresses with caching.
        """
        if not self.access_token:
            return None

        cache_key = f"github_emails:{self.pk}"
        emails = cache.get(cache_key)

        if emails is None or force_refresh:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = requests.get(settings.GITHUB_OAUTH2_EMAILS_URL, headers=headers)
            if response.status_code == 200:
                emails = response.json()
                cache.set(cache_key, emails, timeout=60 * 15)  # cache for 15 minutes
        return emails

    def update_user_profile(self, force_refresh=False):
        """
        Update the user's profile information from GitHub.
        """
        github_data = self.fetch_github_data(force_refresh=force_refresh)
        if not github_data:
            return

        self.raw_data = github_data
        self.name = github_data.get("name", self.name)
        self.uid = str(github_data.get("id", self.uid))
        self.username = github_data.get("login", self.username)
        self.avatar_url = github_data.get("avatar_url", self.avatar_url)
        self.bio = github_data.get("bio", self.bio)
        self.save()

        emails = self.fetch_github_emails(force_refresh=force_refresh)
        if emails:
            for email in emails:
                if email.get("primary") and email.get("email") and email.get("visibility") == "public":
                    self.email = email.get("email")
                    self.save()
