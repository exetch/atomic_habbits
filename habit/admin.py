from django.contrib import admin
from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'time', 'action', 'is_pleasant', 'linked_habit',
                    'frequency', 'reward', 'duration', 'is_public')
    list_filter = ('time', 'is_pleasant', 'linked_habit', 'frequency', 'duration', 'is_public')
    search_fields = ('user', 'action', 'reward')
