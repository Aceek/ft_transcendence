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
