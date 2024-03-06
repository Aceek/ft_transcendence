import asyncio
import time

from .ball import Ball
from .player import Player
from .config import *
from .enum import GameStatus
from .sync import GameSync
from .channel_com import ChannelCom
from .database_ops import DatabaseOps
from ..redis.redis_ops import RedisOps


class GameLogic:
    def __init__(self, consumers):
        self.room_name = consumers.room_name
        self.room_group_name = consumers.room_group_name
        self.mode = consumers.game_mode
        self.player_nb = consumers.player_nb
        self.type = consumers.game_type
        if self.type == "tournament":
            self.tournament_id = consumers.tournament_id
        else:
            self.tournament_id = "none"

        #debug print
        print(f"Room Name: {self.room_name}")
        print(f"Room Group Name: {self.room_group_name}")
        print(f"Game Mode: {self.mode}")
        print(f"Number of Players: {self.player_nb}")
        print(f"Game Type: {self.type}")
        if hasattr(consumers, 'tournament_id') and self.tournament_id:
            print(f"Tournament ID: {self.tournament_id}")
        else:
            print("Tournament ID: Not applicable")
        
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        if self.player_nb > 2:
            self.screen_width = self.screen_height

        self.paddle_height = PADDLE_HEIGHT
        self.paddle_width = PADDLE_WIDTH
        self.paddle_speed = PADDLE_SPEED
        self.paddle_border_distance = PADDLE_BORDER_DISTANCE
        self.ball_size = BALL_SIZE
        self.ball_speed = BALL_SPEED

        self.score_start = SCORE_START
        self.score_limit = SCORE_LIMIT

        self.players = []
        self.ball = None
        self.winner = None

    # -------------------------------INIT-----------------------------------

    def init_static_data(self):
        static_data = {
            "ballSize": self.ball_size,
            "paddleWidth": self.paddle_width,
            "paddleHeight": self.paddle_height,
            "paddleSpeed": self.paddle_speed,
            "canvasHeight": self.screen_height,
            "canvasWidth": self.screen_width,
            "gameID": self.room_name,
            "gameMode": self.mode,
            "playerNb": self.player_nb,
            "gameType": self.type,
            "tournamentId": self.tournament_id
        }
        return static_data

    
    async def init_env(self):
        """Initial env setup."""
        self.redis_ops = await RedisOps.create(self.room_name)
        self.channel_com = ChannelCom(self.room_group_name)
        self.game_sync = GameSync(self)
        self.database_ops = DatabaseOps()

    async def init_game(self):
        """Initial game setup."""
        # Init static data
        self.static_data = self.init_static_data() 
        await self.redis_ops.set_static_data(self.static_data)

        await self.get_static_data_and_send()

    async def init_objects(self):
        """Initial game setup."""
        
        # Init players
        await self.init_players()

        # Init ball
        self.ball = Ball(self) 
        await self.ball.set_data_to_redis()

        await self.get_dynamic_data_and_send()

    async def init_players(self):
        """Initializes player objects with position and associated CustomUser."""
        users_id = await self.redis_ops.get_connected_users_ids()
        for user_id in users_id:
            custom_user = await self.database_ops.get_custom_user(user_id)
            if custom_user is not None:
                position = await self.redis_ops.get_player_position(user_id)
                if position is not None:
                    player = Player(position, self, custom_user)
                    await player.set_data_to_redis()
                    self.players.append(player)
                else:
                    print(f"Unknown position received for user ID {user_id}: {position}")

    async def reset_players(self):
        for player in self.players:
            player.reset_value()
            await player.set_data_to_redis()
        self.winner = None

    async def get_winner_by_forfeit(self):
        """Determine the winner by forfeit based on the remaining connected player."""
        connected_users_ids = await self.redis_ops.get_connected_users_ids()
        if connected_users_ids:
            winner_id = connected_users_ids[0]
            print(f"Assigning winner by default due to disconnection: {winner_id}")
            for player in self.players:
                if str(player.user.id) == str(winner_id):  # Ensure matching ID types (both as strings)
                    self.winner = player
                    return player
        else:
            return None

    # ---------------------------DATA UPDATES-----------------------------------

    async def get_static_data_and_send(self):
        """Centralized method to send dynamic data."""
        static_data = await self.redis_ops.get_static_data()
        await self.channel_com.send_static_data(static_data)

    async def get_dynamic_data_and_send(self):
        """Centralized method to send dynamic data."""
        dynamic_data = await self.redis_ops.get_dynamic_data()
        await self.channel_com.send_dynamic_data(dynamic_data)

    async def update_game_status_and_notify(self, new_status):
        """Updates game status and sends dynamic data if necessary."""
        await self.redis_ops.set_game_status(new_status)
        await self.get_dynamic_data_and_send()

    # -------------------------------LAUNCHER-----------------------------------

    async def launch_game(self):
        """Launch game."""
        await self.update_game_status_and_notify(GameStatus.NOT_STARTED)    
        await self.game_sync.countdown()

        # If a client disconnect during the countdown, the launchher  restart to wait for a reconnection
        if await self.redis_ops.get_game_status() == GameStatus.SUSPENDED:
            if await self.game_sync.wait_for_players_to_start(True):
                await self.launch_game()
        
        await self.update_game_status_and_notify(GameStatus.IN_PROGRESS)
        self.last_update_time = time.time()

    # -------------------------CHECK GAME STATE-----------------------------------

    async def is_game_active(self):
        current_status = await self.redis_ops.get_game_status()
        
        if current_status == GameStatus.COMPLETED:
            return False
        elif current_status == GameStatus.SUSPENDED:
            # Notify all the clients the game is suspendended
            await self.get_dynamic_data_and_send()
            return await self.is_game_resuming()
        return True

    async def is_game_resuming(self):
        print("Checking if the game is resuming...")
        if await self.game_sync.wait_for_players_to_start(True):
            await self.launch_game()
            return True

        await self.update_game_status_and_notify(GameStatus.COMPLETED)
        return False

    # -------------------------------LOOP-----------------------------------

    async def run(self):
        """Running the task"""
        await self.init_env()
        await self.init_game()

        if await self.game_sync.wait_for_players_to_start(False):
            # Send the initial data to all new connected users
            await self.get_static_data_and_send()
            await self.init_objects()
            await self.game_loop()

    async def game_loop(self):
        """The main game loop."""
        await self.launch_game()
        target_loop_duration = 1 / TICK_RATE

        try:
            print("Game loop started.")
            while True:
                loop_start_time = time.time()
                current_time = time.time()
                delta_time = current_time - self.last_update_time
                self.last_update_time = current_time

                if not await self.is_game_active():
                    break

                await self.game_tick(delta_time)

                # Calculate the remaining tick time to send the data at fixed interval
                loop_execution_time = time.time() - loop_start_time
                sleep_duration = max(0, target_loop_duration - loop_execution_time)
                
                await asyncio.sleep(sleep_duration)

            # Handle the case of a forfeit, the winner is the remaining player
            if self.winner is None:
                self.winner = await self.get_winner_by_forfeit()
            await self.database_ops.update_match_history(self.winner, self.players)

            # Only try to restart the match for standard games
            if self.type == "standard":
                if await self.game_sync.wait_for_players_to_restart():
                    await self.redis_ops.del_all_restart_requests()
                    await self.reset_players()
                    await self.game_loop()
            
        except asyncio.CancelledError:
             print("Game loop cancelled. Performing cleanup.")
        except Exception as e:
              print(f"An unexpected error occurred: {e}")
        finally:
            await self.redis_ops.clear_all_data()
            print("All Redis room data cleared successfully.")


    async def game_tick(self, delta_time):
        """Perform a single tick of the game lop."""
        # Update the ball position in fucntion on vellocity and delta time
        self.ball.update_position(delta_time)

        # Check and handle wall collision
        if self.ball.check_wall_collision():
            self.ball.handle_wall_bounce()

        # Retrieve paddle position from players
        for player in self.players:
            await player.get_paddle_from_redis()

        # Check and handle paddle collision
        collision, player = self.ball.check_paddle_collision(self.players)
        if collision:
            self.ball.handle_paddle_bounce_calculation(player.position, self.players)
        
        # Check and handle goal scored
        scored, player = self.ball.check_score()
        if scored:
            self.ball.reset_value()
            if player is not None:
                await player.update_score()
                if player.check_win():
                    self.winner = player
                    await self.update_game_status_and_notify(GameStatus.COMPLETED)

        # Set the ball data to Redis
        await self.ball.set_data_to_redis()

        # Broadcast the current game data to all clients
        await self.get_dynamic_data_and_send()
        