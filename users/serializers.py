from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """ "Сериализатор для пользователя"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "city"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        """Метод для обновления пароля пользователя"""
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)

        return super().update(instance, validated_data)


class PublicUserSerializer(serializers.ModelSerializer):
    """ "Сериализатор для пользователя при публичном просмотре"""

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "avatar", "city"]
