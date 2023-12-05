from rest_framework import serializers
from .models import Habit
from .validators import validate_duration, validate_habit_data


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_duration(self, value):
        return validate_duration(value)

    def validate(self, data):
        return validate_habit_data(data)
