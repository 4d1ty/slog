from django.contrib import admin
from .models import WebGame

@admin.register(WebGame)
class WebGameAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at", "is_approved")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "author", "extracted_path")
    list_editable = ("is_approved",)

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        super().save_model(request, obj, form, change)