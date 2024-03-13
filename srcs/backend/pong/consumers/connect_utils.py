def get_user_id(scope):
    return str(scope["user"].id if scope["user"].is_authenticated else "anonymous")

def get_username(scope):
    return str(scope["user"].username if scope["user"].is_authenticated else "anonymous")

def get_game_mode(scope):
    return scope["url_route"]["kwargs"]["mode"]

def get_number_of_players(scope):
    return int(scope["url_route"]["kwargs"]["players"])

def get_game_type(scope):
    return scope["url_route"]["kwargs"]["type"]

def get_room_names(scope):
    room_name = scope["url_route"]["kwargs"]["room_id"]
    room_group_name = f"pong_room_{room_name}"
    return room_name, room_group_name
