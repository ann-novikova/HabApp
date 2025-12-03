from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .apps import HabitsConfig
from .views import HabitViewSet, PublicHabitListViewSet

app_name = HabitsConfig.name

router = SimpleRouter()

router.register("my_habits", HabitViewSet, basename="my_habit")
router.register("public_habits", PublicHabitListViewSet, basename="public_habit")

urlpatterns = [
    path("", include(router.urls)),
]
