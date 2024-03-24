import asyncio
import time

from .config import *
from .enum import GameStatus
from .init import GameInitializer

from .ball import Ball
from .player import Player
from .sync import GameSync
from .channel_com import ChannelCom
from ..database.database_ops import DatabaseOps
from ..redis.redis_ops import RedisOps

class GameLogic:
    def __init__(self, consumers):
        self.consumers = consumers
        self.room_name = consumers.room_name
        self.room_group_name = consumers.room_group_name
        self.mode = consumers.game_mode
        self.player_nb = consumers.player_nb
        self.type = consumers.game_type

        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT

        self.paddle_height = PADDLE_HEIGHT
        self.paddle_width = PADDLE_WIDTH
        self.paddle_speed = PADDLE_SPEED
        self.paddle_border_distance = PADDLE_BORDER_DISTANCE
        self.ball_size = BALL_SIZE
        self.ball_speed = BALL_SPEED
        self.ball_speed_max= BALL_SPEED_MAX
        self.ball_speed_increase = BALL_SPEED_INCREASE
        
        if self.player_nb > 2:
            self.screen_width = self.screen_height
            self.ball_speed =\
                round(self.ball_speed * (self.screen_width / SCREEN_WIDTH))

        self.score_start = SCORE_START
        self.score_limit = SCORE_LIMIT

        self.players = []
        self.ball = None
        self.winner = None

        self.ball_compacted_data = []
        self.players_compacted_data = []

        self.match = None
        self.tournament = None
        self.tournament_id = ""

        self.target_loop_duration = 1 / TICK_RATE
        self.loop_count = 0
        self.loop_count_reset_time = time.time()

        self.redis_ops = None
        self.initializer = GameInitializer(self)
        self.task = None
        self.cleanup_done = False

    # ---------------------------DATA UPDATES-----------------------------------

    async def get_and_send_compacted_dynamic_data(self, process_time):
        ball_compacted_data = []
        players_compacted_data = []

        ball_compacted_data = self.ball.get_dynamic_compacted_ball_data()
        for player in self.players:
            players_compacted_data.append(player.get_dynamic_compacted_player_data())

        await self.channel_com.send_compacted_dynamic_data(ball_compacted_data, players_compacted_data, process_time)

    async def get_and_send_static_data(self):
        static_data = await self.redis_ops.get_static_data()
        await self.channel_com.send_static_data(static_data)

    async def get_and_send_dynamic_data(self):
        dynamic_data = await self.redis_ops.get_dynamic_data()
        await self.channel_com.send_dynamic_data(dynamic_data)

    async def update_game_status_and_notify(self, new_status):
        await self.redis_ops.set_game_status(new_status)
        await self.get_and_send_dynamic_data()

    # -------------------------CHECK GAME STATE-----------------------------------

    async def is_game_active(self):
        current_status = await self.redis_ops.get_game_status()
        
        if current_status == GameStatus.COMPLETED:
            return False
        elif current_status == GameStatus.SUSPENDED:
            # Update the last ball position to redis and
            # notify all the clients the game is suspendended
            await self.ball.set_data_to_redis()
            await self.get_and_send_dynamic_data()
            return await self.is_game_resuming()
        return True

    async def is_game_resuming(self):
        if await self.game_sync.wait_for_players_to_resume():
            await self.launch_game()
            return True

        await self.update_game_status_and_notify(GameStatus.COMPLETED)
        return False
    
    # -------------------------------LAUNCHER-----------------------------------

    async def run(self):
        try:
            await self.initializer.init_env()
            await self.initializer.init_static_data()
            await self.update_game_status_and_notify(GameStatus.UNSTARTED)

            if await self.game_sync.wait_for_players_to_start():
                await self.initializer.init_objects()
                await self.game_loop()
            else:
                # Clear data to reset the room in tournament case
                await self.perform_cleanup()
        
        except Exception as e:
            print(f"An unexpected error occurred during run: {e}")
            await self.perform_cleanup()

    async def launch_game(self):
        await self.update_game_status_and_notify(GameStatus.LAUNCHING)    
        await self.game_sync.countdown()

        # If a client disconnect during the countdown, the launcher  restart to wait for a reconnection
        if await self.redis_ops.get_game_status() == GameStatus.SUSPENDED:
            # Notify all the clients the game is suspendended
            await self.get_and_send_dynamic_data()
            if await self.is_game_resuming():
                await self.update_game_status_and_notify(GameStatus.IN_PROGRESS)
        else:
            await self.update_game_status_and_notify(GameStatus.IN_PROGRESS)
        self.last_update_time = time.time()

    # -------------------------------LOOP-----------------------------------

    async def game_loop(self):
        await self.launch_game()

        try:
            while await self.is_game_active():
                loop_start_time = time.time()

                # Calculate delta time
                delta_time = loop_start_time - self.last_update_time
                self.last_update_time = loop_start_time

                # Perform game updates
                operation_times, process_time = await self.game_tick(delta_time)

                # Broadcast the game data to all clients
                await self.get_and_send_compacted_dynamic_data(process_time)

                # Log process time and operation times if necessary
                if process_time > 10:
                    print(f"PROCESS TIME : {process_time}")
                    for op_time in operation_times:
                        print(op_time)

                # Sleep to maintain the target loop duration
                sleep_duration = max(0, self.target_loop_duration - (time.time() - loop_start_time))
                await asyncio.sleep(sleep_duration)
            
            await self.handle_game_end()

        except asyncio.CancelledError:
             print("Game loop cancelled. Performing cleanup.")
        except Exception as e:
              print(f"An unexpected error occurred during game loop: {e}")
        finally:
            await self.perform_cleanup()

    async def game_tick(self, delta_time):
        # Initialize an array to store operation times
        operation_times = []

        # Update ball position
        start_time = time.time()
        self.ball.update_position(delta_time)
        start_process_time = time.time()
        operation_times.append({'operation': 'update_position', 'delta_time': (time.time() - start_time) * 1000})

        # Check and handle wall collision
        start_time = time.time()
        if self.ball.check_wall_collision():
            self.ball.handle_wall_bounce()
        operation_times.append({'operation': 'check_wall_collision', 'delta_time': (time.time() - start_time) * 1000})

        # Retrieve paddle position from players
        for player in self.players:
            start_time = time.time()
            await player.get_paddle_from_redis()
            operation_times.append({'operation': f'get_paddle_from_redis_{player.id}', 'delta_time': (time.time() - start_time) * 1000})

        # Check and handle paddle collision
        start_time = time.time()
        collision, player = self.ball.check_paddle_collision(self.players)
        if collision:
            self.ball.handle_paddle_bounce_calculation(player)
        operation_times.append({'operation': 'check_paddle_collision', 'delta_time': (time.time() - start_time) * 1000})

        # Check and handle goal scored
        start_time = time.time()
        scored, player = self.ball.check_score()
        if scored:
            self.ball.reset_value()
            if player is not None:
                await player.update_score()
                await self.get_and_send_dynamic_data()
                if player.check_win():
                    self.winner = player
                    await self.update_game_status_and_notify(GameStatus.COMPLETED)
        operation_times.append({'operation': 'check_score', 'delta_time': (time.time() - start_time) * 1000})

        # This could also be returned if you need to use it outside this function
        return operation_times, (time.time() - start_process_time) * 1000

    # -------------------------------END GAME-----------------------------------

    async def handle_game_end(self):
        # Handle the case of a forfeit, the winner is the remaining player
        if self.winner is None:
            self.winner = await self.get_winner_by_forfeit()

        # Only try to restart the game for standard games
        if self.type == "standard":
            # Feature currenlty not working for 2+ players
            if self.player_nb < 3:
                if self.winner is not None:
                    await self.database_ops.update_match_history(self.winner, self.players)
            if await self.game_sync.wait_for_players_to_restart():
                await self.redis_ops.del_all_restart_requests()
                await self.reset_players()
                await self.game_loop()
        elif self.type == "tournament":
            if self.winner is not None:
                    await self.database_ops.update_tournament(self.mode, self.match, self.tournament, self.winner)
            await self.game_sync.wait_to_exit(GameStatus.COMPLETED)
        

    async def reset_players(self):
        for player in self.players:
            player.reset_value()
            await player.set_data_to_redis()

    async def get_winner_by_forfeit(self):
        connected_users_ids = await self.redis_ops.get_connected_users_ids()
        if connected_users_ids:
            winner_id = connected_users_ids[0]
            for player in self.players:
                if str(player.user.id) == str(winner_id):  # Ensure matching ID types (both as strings)
                    self.winner = player
                    return player
        else:
            return None
        
    # -------------------------------CLEAN-----------------------------------

    async def perform_cleanup(self):
        if not self.cleanup_done:
            if self.redis_ops is not None:
                await self.redis_ops.clear_all_data()
            await self.cleanup_task()
            self.cleanup_done = True

    async def cleanup_task(self):
        if hasattr(self, 'task') and self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                print("Task cancelled successfully.")
