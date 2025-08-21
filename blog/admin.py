from django.contrib import admin
from .models import Post, Tag, Reaction, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at", "webgame")
    search_fields = ("title", "content")
    list_filter = ("created_at", "updated_at", "author")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["tags", "reactions", "webgame"]

    def save_model(self, request, obj, form, change):
        obj.author = request.user
        print(f"Saving post: {obj.title} by {obj.author}")
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).filter(author=request.user)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("content",)
    autocomplete_fields = ["post", "author", "parent", "reactions"]
    list_filter = ("created_at", "author")
    fields = ["post", "author", "content", "parent", "reactions"]
    readonly_fields = ["created_at"]


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "reaction_type")
    search_fields = ("user__username", "reaction_type")
    list_filter = ("reaction_type",)
    autocomplete_fields = ["user"]
