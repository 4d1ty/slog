from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from webgame.models import WebGame
NOT_ALLOWED_SLUGS = ["admin", "login", "logout", "register", "create", "edit", "delete"]

class Post(models.Model):
    """
    Model to represent a blog post.
    """
    title = models.CharField(max_length=255, help_text="Title of the blog post")
    slug = models.SlugField(max_length=255, unique=True, help_text="Slug for the blog post")
    content = models.TextField(help_text="Content of the blog post")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts', help_text="Author of the post")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation date and time of the post")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update date and time of the post")
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts', help_text="Tags associated with the post")
    reactions = models.ManyToManyField('Reaction', blank=True, related_name='posts', help_text="Reactions to the post")
    webgame = models.ForeignKey(WebGame, on_delete=models.SET_NULL, related_name='posts', help_text="Web game associated with the post", null=True, blank=True)

    is_published = models.BooleanField(default=True, help_text="Whether the post is published or not")
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.slug in NOT_ALLOWED_SLUGS:
            raise ValidationError(f"Slug '{self.slug}' is not allowed.")

class Tag(models.Model):
    """
    Model to represent a tag for blog posts.
    """
    name = models.CharField(max_length=50, unique=True, help_text="Name of the tag")
    slug = models.SlugField(max_length=50, unique=True, help_text="Slug for the tag")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Model to represent a comment on a blog post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', help_text="Post that the comment belongs to")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', help_text="Parent comment if this is a reply")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments', help_text="Author of the comment")
    content = models.TextField(help_text="Content of the comment")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation date and time of the comment")
    reactions = models.ManyToManyField('Reaction', blank=True, related_name='comments', help_text="Reactions to the comment")

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

    def get_tree(self):
        """
        Get the comment thread tree.
        """
        tree = []
        if self.replies.exists():
            for reply in self.replies.all():
                tree.append(reply)
                tree.extend(reply.get_tree())
        return tree

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ["-created_at"]


class Reaction(models.Model):
    """
    Model to represent a reaction (like/dislike) on a blog post or comment.
    """
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions', help_text="User who made the reaction")
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, help_text="Type of reaction")

    class Meta:
        verbose_name = "Reaction"
        verbose_name_plural = "Reactions"
        ordering = ["-id"]
