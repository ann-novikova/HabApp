from rest_framework import serializers

from .models import Habit
from .validators import HabitValidator


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("owner",)
        validators = [HabitValidator()]
        extra_kwargs = {"time": {"input_formats": ["%H:%M", "%H:%M:%S"]}}
