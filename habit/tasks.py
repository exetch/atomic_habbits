from celery import shared_task
from config import settings
from django.utils import timezone
from .models import Habit, HabitCompletion
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
        Отправляет напоминания о привычках пользователям через Telegram.
    """
    due_habits = get_due_habits()
    for habit in due_habits:
        if habit.user.telegram_profile.exists():
            chat_id = habit.user.telegram_profile.first().chat_id
            message = f"Напоминание: {habit.action} в {habit.location} в {habit.time.strftime('%H:%M')}"
            send_telegram_message(chat_id, message, bot_token)
            record_habit_completion(habit)

def get_due_habits():
    """
        Возвращает список привычек, для которых пора отправить напоминание.

        Определяет привычки, время выполнения которых находится в пределах
        ближайших 10 минут от текущего времени. Также учитывает частоту и историю
        выполнения привычек, чтобы избежать повторных напоминаний о тех привычках,
        которые уже выполнены в соответствии с их частотой.

        Возвращает:
            List[Habit]: Список привычек, для которых следует отправить напоминание.
    """
    now = timezone.now()
    ten_minutes_from_now = now + timezone.timedelta(minutes=10)
    due_habits = []

    for habit in Habit.objects.filter(time__gte=now.time(), time__lte=ten_minutes_from_now.time()):
        last_completion = habit.completions.order_by('-completion_date').first()
        if not last_completion or (now.date() - last_completion.completion_date).days >= habit.frequency:
            due_habits.append(habit)
    return due_habits


def record_habit_completion(habit):
    """
    Создает запись об исполнении привычки в HabitCompletion.

    Аргументы:
        habit (Habit): Объект привычки, для которой необходимо записать исполнение.
    """
    HabitCompletion.objects.create(habit=habit, completion_date=timezone.now().date())
