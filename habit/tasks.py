from celery import shared_task
from config import settings
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import Habit
from .telegram_utils import get_updates, send_telegram_message

bot_token = settings.TELEGRAM_API_TOKEN


@shared_task
def receiving_email_for_telegram_binding():
    """
        Периодическая задача Celery для получения email и связи Telegram аккаунтов.

        Запускает процесс получения обновлений от Telegram бота и обрабатывает
        сообщения, содержащие email, для связи аккаунтов пользователей с их
        Telegram chat_id.
    """
    bot_token = settings.TELEGRAM_API_TOKEN
    get_updates(bot_token)


@shared_task
def check_and_send_reminders():
    """
        Задача Celery для отправки напоминаний о привычках пользователям в Telegram.

        Определяет привычки, время выполнения которых приближается, и отправляет
        соответствующие напоминания в Telegram чаты пользователей, если у них
        связаны Telegram аккаунты.
    """
    habits = get_upcoming_habits()
    for habit in habits:
        if habit.user.telegram_profile.exists():
            chat_id = habit.user.telegram_profile.first().chat_id
            message = f"Напоминание: {habit.action} в {habit.location} " \
                      f"в {habit.time.strftime('%H:%M')}"
            send_telegram_message(chat_id, message, bot_token)


def get_upcoming_habits():
    """
        Возвращает список привычек, время выполнения которых приближается.

        Определяет привычки, которые должны быть выполнены в ближайшие 9 минут.
        Используется для определения, какие напоминания должны быть отправлены.

        Возвращает:
            List[Habit]: Список объектов привычек, подходящих для отправки напоминаний.
    """
    now = make_aware(datetime.now())
    nine_minutes_from_now = now + timedelta(minutes=9)

    upcoming_habits = Habit.objects.filter(
        time__gte=now,
        time__lte=nine_minutes_from_now
    )
    return upcoming_habits
