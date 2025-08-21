from django.shortcuts import render
from blog.models import Post
from webgame.models import WebGame
def index(request):
    posts = Post.objects.filter(is_published=True)[:5]  # Limit to 5 posts for the homepage
    games = WebGame.objects.filter(is_approved=True)[:5]  # Limit to 5 games for the homepage
    return render(request, 'index.html', {'posts': posts, 'games': games})