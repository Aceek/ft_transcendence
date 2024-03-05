def get_user_id(scope):
    """Determine the user ID based on authentication status."""
    return str(scope["user"].id if scope["user"].is_authenticated else "anonymous")

def get_room_names(scope):
    """Generate room and group names based on the game UID."""
    room_name = scope["url_route"]["kwargs"]["uid"]
    room_group_name = f"pong_room_{room_name}"
    return room_name, room_group_name

def get_game_mode(scope):
    """Retrieve the game mode from the URL path."""
    return scope["url_route"]["kwargs"]["mode"]

def get_number_of_players(scope):
    """Retrieve the number of players from the URL path."""
    return int(scope["url_route"]["kwargs"]["players"])
