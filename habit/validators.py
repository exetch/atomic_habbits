from rest_framework import serializers

from habit.models import Habit


def validate_duration(value):
    """Проверка продолжительности выполнения привычки."""
    if value > 120:
        raise serializers.ValidationError("Продолжительность выполнения привычки не должна превышать 120 секунд.")
    return value


def validate_habit_data(data):
    """Общая валидация данных привычки."""
    if data.get('linked_habit') and data.get('reward'):
        raise serializers.ValidationError(
            "Нельзя одновременно выбрать связанную привычку и указать вознаграждение.")

    if data.get('is_pleasant') and (data.get('reward') or data.get('linked_habit')):
        raise serializers.ValidationError(
            "У приятной привычки не может быть вознаграждения или связанной привычки.")

    frequency = data.get('frequency')
    if frequency is not None and frequency > 7:
        raise serializers.ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")

    linked_habit = data.get('linked_habit')
    if linked_habit:
        linked_habit_instance = Habit.objects.filter(id=linked_habit.id, is_pleasant=True).first()
        if not linked_habit_instance:
            raise serializers.ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной привычки.")

    return data
