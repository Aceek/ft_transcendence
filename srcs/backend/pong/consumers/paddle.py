from ..game.config import SCREEN_HEIGHT, PADDLE_HEIGHT, PADDLE_SPEED

class Paddle:
    def __init__(self, room_name, user_id, redis_ops):
        self.room_name = room_name
        self.user_id = user_id
        self.redis_ops = redis_ops
        self.side = None

    async def assignment(self):
        positions = ['left', 'right']
        paddle_position_keys = {pos: f"game:{self.room_name}:paddle:{pos}" for pos in positions}

        for position, key in paddle_position_keys.items():
            if await self.redis_ops.connection.sismember(key, self.user_id):
                self.side = position
                break
        else:
            for position, key in paddle_position_keys.items():
                if not await self.redis_ops.connection.scard(key):
                    await self.redis_ops.connection.sadd(key, self.user_id)
                    self.side = position
                    break

        # Assuming you have a method to notify about paddle side assignment
        print(f"User {self.user_id} assigned to {self.side} paddle")

    async def check_movement(self, side, new_y):
        if new_y < 0:
            print(f"Requested paddle move for {side} is below 0. Clamping to 0.")
            return False
        elif new_y > SCREEN_HEIGHT - PADDLE_HEIGHT:
            print(f"Requested paddle move for {side} exceeds screen height. Clamping to {SCREEN_HEIGHT - PADDLE_HEIGHT}.")
            return False

        current_y = await self.redis_ops.get_dynamic_value(self.room_name, f"{side[0]}p_y")
        current_y = int(current_y) if current_y is not None else 0

        y_diff = abs(new_y - current_y)
        if y_diff <= PADDLE_SPEED:
            return True
        else:
            print(f"Attempted to move the {side} paddle more than the speed limit.")
            return False
