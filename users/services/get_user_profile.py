from users.models import CustomUser as User





def get_user_profile(user_id):
    try:
        user = User.objects.get(id=user_id)
        return {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "address": user.address,
            "image": user.image.url if user.image else None
        }
    except User.DoesNotExist:
        return None