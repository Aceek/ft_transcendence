async def attempt_to_start_game(redis_ops, room_name):
	flag_key = f"game:{room_name}:logic_flag"
	flag_set = await redis_ops.connection.setnx(flag_key, "true")
	if flag_set:
		await redis_ops.connection.expire(flag_key, 60)
		return True
	return False

