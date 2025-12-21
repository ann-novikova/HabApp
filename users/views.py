from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.permissions import UserIsOwner
from users.serializers import PublicUserSerializer, UserSerializer


class UserListApiView(ListAPIView):
    """Контроллер для вывода пользователей с историей платежей"""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PublicUserSerializer


class UserRetriveApiView(RetrieveAPIView):
    """Контроллер для просмотра данных о пользователе"""

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        obj = self.get_object()

        if self.request.user == obj:
            return UserSerializer

        return PublicUserSerializer


class UserUpdateApiView(UpdateAPIView):
    """Контроллер для редактирования данных пользователя"""

    queryset = User.objects.all()
    permission_classes = (
        UserIsOwner,
        IsAuthenticated,
    )
    serializer_class = UserSerializer


class UserDestroyApiView(DestroyAPIView):
    """Контроллер для удаления данных пользователя"""

    queryset = User.objects.all()
    permission_classes = (
        UserIsOwner,
        IsAuthenticated,
    )
    serializer_class = UserSerializer


class UserCreateApiView(CreateAPIView):
    """Контроллер для создания пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Метод для создания пользователя"""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
