from rest_framework import serializers
from .models import CUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CUser
        exclude = ['groups', 'user_permissions', 'is_staff', 'is_superuser', 'following']
        read_only_fields = ['last_login', 'is_active', 'number_of_following']
        extra_kwargs = {
            'password': {'write_only': True},
            'following': {'write_only': True}
        }

    def create(self, validated_data):
        user: CUser = CUser(**validated_data)
        user.set_password(validated_data.get('password'))
        user.is_active = False
        user.save()
        return user


# follow user serializer
class FollowActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
