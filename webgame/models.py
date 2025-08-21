import shutil
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
import os
import zipfile

def validate_file_size(value):
    """Limit file upload size to 5MB."""
    limit = 5 * 1024 * 1024  # 5 MB
    if value.size > limit:
        raise ValidationError(f"Max file size is {limit / (1024*1024)} MB")

def game_upload_path(instance, filename):
    """Upload zip to media/games/<slug>/"""
    return f"games/{slugify(instance.title)}/{filename}"

class WebGame(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    zip_file = models.FileField(
        upload_to=game_upload_path,
        blank=True,
        null=True,
        help_text="Upload a ZIP file containing your game build",
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=["zip"]),
        ],
    )
    extracted_path = models.FileField(
        blank=True,
        help_text="Auto-filled path to extracted index.html"
    )
    url = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Optional URL to the game if hosted externally",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webgames",
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if not self.zip_file and not self.url:
            raise ValidationError("You must upload a ZIP file or provide a game URL.")
        if self.zip_file and not self.zip_file.name.endswith(".zip"):
            raise ValidationError("Uploaded file must be a ZIP archive.")
        if self.url and not self.url.startswith(("http://", "https://")):
            raise ValidationError("Game URL must start with http:// or https://")
        if self.url and self.zip_file:
            raise ValidationError("You cannot provide both a ZIP file and a game URL.")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

        # Handle zip extraction
        if self.zip_file and self.zip_file.name.endswith(".zip"):
            zip_path = self.zip_file.path
            extract_to = os.path.join(settings.MEDIA_ROOT, "games", self.slug)
            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_to)

            index_path = os.path.join(extract_to, "index.html")
            if os.path.exists(index_path):
                # URL path for iframe
                self.extracted_path = f"games/{self.slug}/index.html"
                super().save(update_fields=["extracted_path"])

    def delete(self, *args, **kwargs):
        """
        Delete the entire game folder in /media/games/<slug>/ along with all its contents.
        """
        if self.slug:
            game_dir = os.path.join(settings.MEDIA_ROOT, "games", self.slug)
            if os.path.exists(game_dir):
                shutil.rmtree(game_dir)
        super().delete(*args, **kwargs)

    @property
    def source(self):
        """Return the URL for iframe embed."""
        if self.zip_file:
            return self.extracted_path.url
        elif self.url:
            return self.url
        return None

    def __str__(self):
        return self.title
