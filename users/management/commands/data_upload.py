from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Засеивание БД тестовыми данными"
    users_test_data = [
        {
            "email": "admin1@mail.ru",
            "is_staff": True,
            "is_active": True,
            "is_superuser": True,
            "password": "12345",
        },
        {
            "email": "admin2@mail.ru",
            "is_staff": True,
            "is_active": True,
            "is_superuser": False,
            "password": "12345",
        },
        {
            "email": "admin3@mail.ru",
            "is_staff": True,
            "is_active": True,
            "is_superuser": False,
            "password": "12345",
        },
    ]

    def handle(self, *args, **kwargs):

        for data_user in self.users_test_data:
            get_user = User.objects.filter(email=data_user["email"])
            if not get_user:
                user: User = User.objects.create(
                    email=data_user["email"],
                    is_staff=data_user["is_staff"],
                    is_active=data_user["is_active"],
                    is_superuser=data_user["is_superuser"],
                )
                user.set_password(data_user["password"])
                user.save()
        self.stdout.write(self.style.SUCCESS("Создание данных в БД выполнено успешно"))
