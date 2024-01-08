from django.shortcuts import render

def pong_game(request):
    # Your game logic here
    return render(request, 'pong/pong_game.html')
