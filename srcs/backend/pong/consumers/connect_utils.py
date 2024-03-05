def get_user_id(scope):
    """Determine the user ID based on authentication status."""
    return str(scope["user"].id if scope["user"].is_authenticated else "anonymous")

def get_game_mode(scope):
    """Retrieve the game mode from the URL path."""
    return scope["url_route"]["kwargs"]["mode"]

def get_number_of_players(scope):
    """Retrieve the number of players from the URL path."""
    return int(scope["url_route"]["kwargs"]["players"])

def get_game_type(scope):
    """Retrieve the game type (standard or tournament) from the URL path."""
    return scope["url_route"]["kwargs"]["type"]

def get_tournament_id(scope):
    if 'tournament_id' in scope["url_route"]["kwargs"]:
        return scope["url_route"]["kwargs"]["tournament_id"]

def get_room_names(scope):
    """Generate room and group names based on the game UID."""
    room_name = scope["url_route"]["kwargs"]["uid"]
    room_group_name = f"pong_room_{room_name}"
    return room_name, room_group_name
