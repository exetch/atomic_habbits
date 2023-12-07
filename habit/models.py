from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    location = models.CharField(max_length=255)
    time = models.TimeField()
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)
    linked_habit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='linked_habits')
    frequency = models.IntegerField(default=1)  # Ежедневно по умолчанию
    reward = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.action} в {self.time} в {self.location}"

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=100, unique=True)
    is_account_linked = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='telegram_profile',
                             blank=True, null=True)

    def __str__(self):
        return f"chat_id {self.chat_id}"


class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='completions')
    completion_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Привычка {self.habit.action} выполнена {self.completion_date}"
