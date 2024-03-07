import uuid

def generate_game_url(mode, players, game_type, tournament_id=None, match_id=None):
    # Generate UUIDs as necessary
    room_id = uuid.uuid4()

    base_url = f"/pong/{mode}/{players}/{game_type}"

    if game_type == "tournament":
        # Ensure tournament_id and match_id are provided for tournament games
        if not tournament_id or not match_id:
            raise ValueError("Tournament and match IDs are required for tournament games.")
        url = f"{base_url}/{tournament_id}/{match_id}/{room_id}/"
    elif game_type == "standard":
        url = f"{base_url}/{room_id}/"
    else:
        raise ValueError("Unsupported game type.")

    return url

# Example usage:

# Generate URL for a standard online game
standard_url = generate_game_url(mode="online", players=2, game_type="standard")
print("Standard Game URL:", standard_url)

# Generate URL for an online tournament game
tournament_id = uuid.uuid4()
match_id = uuid.uuid4()
tournament_url = generate_game_url(mode="online", players=2, game_type="tournament", tournament_id=tournament_id, match_id=match_id)
print("Tournament Game URL:", tournament_url)

# Generate URL for a standard offline game
offline_standard_url = generate_game_url(mode="offline", players=2, game_type="standard")
print("Offline Standard Game URL:", offline_standard_url)
