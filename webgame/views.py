from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import WebGameForm
from .models import WebGame
from core.utils import paginate
from django.contrib import messages

@login_required
def game_upload(request):
    if request.method == "POST":
        form = WebGameForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.author = request.user
            game.save()
            messages.success(request, "Game uploaded successfully.")
            return redirect("game_play", slug=game.slug)
    else:
        form = WebGameForm()

    return render(request, "webgame/game_upload.html", {"form": form})


def game_play(request, slug):
    # Either get the approved game or if the game user is request.author just show them their game
    game = get_object_or_404(WebGame, slug=slug)
    if not game.is_approved and game.author != request.user:
        # If the game is not approved and the user is not the author, show a 404
        raise Http404("Game not found")
    return render(request, "webgame/game_play.html", {"game": game})


def game_list(request):
    games = WebGame.objects.filter(is_approved=True)
    page = paginate(request, games)
    return render(request, "webgame/game_list.html", {"games": page})

@login_required
def game_edit(request, slug):
    game = get_object_or_404(WebGame, slug=slug, author=request.user)
    if request.method == "POST":
        form = WebGameForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, "Game updated successfully.")
            return redirect("game_play", slug=game.slug)
    else:
        form = WebGameForm(instance=game)

    return render(request, "webgame/game_edit.html", {"form": form, "game": game})


@login_required
def game_delete(request, slug):
    game = get_object_or_404(WebGame, slug=slug, author=request.user)
    if request.method == "POST":
        game.delete()
        messages.success(request, "Game deleted successfully.")
        return redirect("game_list")
    
    return render(request, "webgame/game_delete.html", {"game": game})