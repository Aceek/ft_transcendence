from rest_framework import exceptions
from CustomUser.models import CustomUser


def remove_friend(user, friends_to_remove):
    for friend_id in friends_to_remove:
        try:
            friend = CustomUser.objects.get(pk=friend_id)
            user.friends.remove(friend)
        except CustomUser.DoesNotExist:
            raise exceptions.NotFound(
                detail="Friend with id {} does not exist".format(friend_id)
            )
    user.save()

def remove_blocked_users(user, blocked_users_to_remove):
    for blocked_user_id in blocked_users_to_remove:
        try:
            blocked_user = CustomUser.objects.get(pk=blocked_user_id)
            user.blocked_users.remove(blocked_user)
        except CustomUser.DoesNotExist:
            raise exceptions.NotFound(
                detail="Blocked user with id {} does not exist".format(blocked_user_id)
            )
    user.save()
