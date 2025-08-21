from django.shortcuts import render, redirect, get_object_or_404
from .forms import PostForm
from .models import Post, Comment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from core.utils import paginate
import json


@login_required
def create_post(request):
    """
    Render the create post page.
    """
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully.")
            return redirect("post_detail", slug=post.slug)
    else:
        form = PostForm()

    return render(request, "blog/create_post.html", {"form": form})


def post_detail(request, slug):
    """
    Render the post detail page.
    """
    post = get_object_or_404(Post, slug=slug)
    post_like_count = post.reactions.filter(reaction_type="like").count()
    post_dislike_count = post.reactions.filter(reaction_type="dislike").count()
    user_liked = post.reactions.filter(user=request.user, reaction_type="like").exists()
    user_disliked = post.reactions.filter(
        user=request.user, reaction_type="dislike"
    ).exists()
    comments = post.comments.filter(parent__isnull=True).select_related("author")

    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")  # optional, for replies
        parent_comment = None
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
        Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent_comment,
        )
        messages.success(request, "Comment added successfully.")
        return redirect("post_detail", slug=slug)

    return render(
        request,
        "blog/post_detail.html",
        {
            "post": post,
            "post_like_count": post_like_count,
            "post_dislike_count": post_dislike_count,
            "user_liked": user_liked,
            "user_disliked": user_disliked,
            "comments": comments,
        },
    )


@login_required
def edit_post(request, slug):
    """
    Render the edit post page.
    """
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully.")
            return redirect("post_detail", slug=post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, "blog/edit_post.html", {"form": form, "post": post})


@login_required
def delete_post(request, slug):
    """
    Render the delete post page.
    """
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("post_list")
    return render(request, "blog/delete_post.html", {"post": post})


@login_required
def post_list(request):
    """
    Render the post list page.
    """
    posts = Post.objects.filter(author=request.user)
    page = paginate(request, posts)
    return render(request, "blog/post_list.html", {"posts": page})


def public_post_list(request):
    """
    Render the public post list page.
    """
    posts = Post.objects.all().order_by("-created_at")
    page = paginate(request, posts)
    return render(request, "blog/public_post_list.html", {"posts": page})


@login_required
def post_react(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    data = json.loads(request.body)
    reaction_type = data.get("reaction_type")
    if reaction_type not in ["like", "dislike"]:
        return JsonResponse({"error": "Invalid reaction"}, status=400)

    post.reactions.filter(user=request.user).delete()

    post.reactions.create(user=request.user, reaction_type=reaction_type)

    # Count reactions
    likes = post.reactions.filter(reaction_type="like").count()
    dislikes = post.reactions.filter(reaction_type="dislike").count()

    return JsonResponse({"likes": likes, "dislikes": dislikes})
