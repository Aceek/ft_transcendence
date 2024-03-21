from .ball import Ball
from .player import Player
from .sync import GameSync
from .enum import PlayerPosition
from .channel_com import ChannelCom
from ..database.database_ops import DatabaseOps
from ..redis.redis_ops import RedisOps

class GameInitializer:
    def __init__(self, game):
        self.game = game

    async def init_env(self):
        self.game.redis_ops = await RedisOps.create(self.game.room_name)
        self.game.channel_com = ChannelCom(self.game.room_group_name)
        self.game.game_sync = GameSync(self.game)
        self.game.database_ops = DatabaseOps()
        self.game.task = self.game.consumers.task
        if self.game.type == "tournament":
            self.game.match, self.game.tournament = \
                await self.game.database_ops.get_match_and_tournament(self.game.room_name)
            if self.game.tournament is not None:
                self.game.tournament_id = str(self.game.tournament.uid)

    def get_static_data(self):
        static_data = {
            "ballSize": self.game.ball_size,
            "paddleWidth": self.game.paddle_width,
            "paddleHeight": self.game.paddle_height,
            "paddleSpeed": self.game.paddle_speed,
            "canvasHeight": self.game.screen_height,
            "canvasWidth": self.game.screen_width,
            "playerNb": self.game.player_nb,
            "gameMode": self.game.mode,
            "gameType": self.game.type,
            "tournamentId": self.game.tournament_id,
        }
        return static_data

    async def init_static_data(self):
        self.game.static_data = self.get_static_data() 
        await self.game.redis_ops.set_static_data(self.game.static_data)
        await self.game.get_and_send_static_data()

    async def init_objects(self):
        await self.init_players()
        self.game.winner = None
        self.game.ball = Ball(self.game) 
        await self.game.ball.set_data_to_redis()
        await self.game.get_and_send_dynamic_data()

    async def init_players(self):
        users_id = await self.game.redis_ops.get_connected_users_ids()
        
        if self.game.mode == "online":
            for user_id in users_id:
                custom_user = await self.game.database_ops.get_custom_user(user_id)
                if custom_user is not None:
                    position = await self.game.redis_ops.get_player_position(user_id)
                    if position is not None:
                        player = Player(position, self.game, custom_user)
                        await player.set_username_to_redis(player.username)
                        await player.set_data_to_redis()
                        self.game.players.append(player)
                    else:
                        print(f"Unknown position for user with ID: {user_id}")
        else:
            custom_user = await self.game.database_ops.get_custom_user(users_id[0])
            positions = [PlayerPosition.LEFT, PlayerPosition.RIGHT]
            for position in positions:
                player = Player(position, self.game, custom_user)
                await player.set_data_to_redis()
                username = f"{player.username} ({str(player.id + 1)})"
                await player.set_username_to_redis(username)
                self.game.players.append(player)
        
        self.game.players.sort(key=lambda player: player.position.value)