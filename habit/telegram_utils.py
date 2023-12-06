from config import settings
from users.models import CustomUser
from habit.models import TelegramUser
import requests


bot_token = settings.TELEGRAM_API_TOKEN


def send_telegram_message(chat_id, message, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.ok


def get_updates(bot_token):
    """
    Получает обновления от Telegram бота и связывает chat_id с пользователями.

    Отправляет запрос к API методу getUpdates, обрабатывает каждое обновление,
    связывая email в тексте сообщения с пользователями системы. При успешном
    нахождении или отсутствии пользователя отправляет уведомление в Telegram чат.

    Аргументы:
        bot_token (str): Токен Telegram бота.

    Возвращает:
        None: Отправляет сообщения в Telegram, не возвращая значений.

    Особенности:
    - Обрабатывает обновления один раз, предотвращая повторные сообщения.
    - Обновляет offset после обработки для исключения дублирования.
    """
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    updates = response.json()

    for update in updates["result"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        telegram_user, created = TelegramUser.objects.get_or_create(
            chat_id=chat_id,
            defaults={'is_account_linked': False}
        )

        if telegram_user.is_account_linked:
            continue

        if text and "@" in text:
            try:
                user = CustomUser.objects.get(email=text)
                telegram_user.user = user
                message = "Ваш аккаунт успешно связан с Telegram."
                telegram_user.is_account_linked = True
            except CustomUser.DoesNotExist:
                message = f"Пользователь с email {text} не найден."

            send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": message}
            requests.post(send_message_url, json=payload)
            telegram_user.save()

    if updates["result"]:
        last_update_id = updates["result"][-1]["update_id"]
        requests.get(f"{url}?offset={last_update_id + 1}")
