from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'address']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value:
                setattr(instance, attr, value)

        if 'image' in validated_data and instance.image:
            instance.image.delete(save=False)

        instance.save()
        return instance
