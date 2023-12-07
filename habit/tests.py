import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APITestCase
from users.models import CustomUser
from .models import Habit, TelegramUser, HabitCompletion
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from unittest import TestCase, mock
from habit.telegram_utils import send_telegram_message, get_updates
from .tasks import check_and_send_reminders, get_due_habits, record_habit_completion
from datetime import timedelta

class HabitAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email='test@mail.com', password='12345')
        self.other_user = CustomUser.objects.create(email='other@mail.com', password='12345')
        self.client.force_authenticate(user=self.user)

        self.linked_habit_pleasant = Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                                                          action="Чтение", duration=30, is_public=True,
                                                          is_pleasant=True)
        self.linked_habit_not_pleasant = Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                                                              action="Работа", duration=30, is_public=True,
                                                              is_pleasant=False)


    def test_create_habit(self):
        url = reverse('habit-list-create')
        data = {"location": "Дом", "time": "08:00:00", "action": "Утренняя пробежка",
                "duration": 20, "is_public": True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)

        # проверка метода __str__
        new_habit = Habit.objects.get(action="Утренняя пробежка")
        self.assertEqual(str(new_habit),
                         f"{new_habit.action} в {new_habit.time.strftime('%H:%M:%S')} в {new_habit.location}")
        TelegramUser.objects.create(
            chat_id='123456789',
            is_account_linked=True,
            user=self.user
        )
        telegram_user = TelegramUser.objects.get(chat_id=123456789)
        expected_object_name = f'chat_id {telegram_user.chat_id}'
        self.assertEqual(expected_object_name, str(telegram_user))

    def test_get_habits(self):
        habit = Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                                     action="Чтение", duration=30, is_public=True)
        response = self.client.get('/habits/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_update_habit(self):
        habit = Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                                     action="Чтение", duration=30, is_public=True)
        data = {"action": "Вечерняя попойка", "location": "Бар", "time": "20:00"}
        response = self.client.put(f'/habits/{habit.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_habit = Habit.objects.get(id=habit.id)
        self.assertEqual(updated_habit.action, "Вечерняя попойка")

    def test_delete_habit(self):
        habit = Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                                     action="Чтение", duration=30, is_public=True)
        response = self.client.delete(f'/habits/{habit.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 2)

    def test_create_habit_unauthenticated(self):
        self.client.logout()
        data = {"location": "Дом", "time": "08:00:00", "action": "Утренняя пробежка",
                "duration": 20, "is_public": True}
        response = self.client.post('/habits/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_habit_invalid_duration(self):
        url = reverse('habit-list-create')
        data = {"location": "Дом", "time": "08:00:00", "action": "Утренняя пробежка",
                "duration": 130, "is_public": True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Продолжительность выполнения привычки не должна превышать 120 секунд.', str(response.data))

    def test_linked_habit_and_reward(self):
        url = reverse('habit-list-create')
        data = {
            "location": "Дом",
            "time": "08:00:00",
            "action": "Утренняя пробежка",
            "duration": 20,
            "is_public": True,
            "linked_habit": self.linked_habit_pleasant.id,
            "reward": "Кофе"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Нельзя одновременно выбрать связанную привычку и указать вознаграждение", str(response.data))

    def test_pleasant_habit_with_reward(self):
        url = reverse('habit-list-create')
        data = {
            "location": "Дом",
            "time": "08:00:00",
            "action": "Утренняя пробежка",
            "duration": 20,
            "is_public": True,
            "is_pleasant": True,
            "reward": "Кофе"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("У приятной привычки не может быть вознаграждения или связанной привычки", str(response.data))

    def test_pleasant_habit_with_linked_habit(self):
        url = reverse('habit-list-create')
        data = {
            "location": "Дом",
            "time": "08:00:00",
            "action": "Утренняя пробежка",
            "duration": 20,
            "is_public": True,
            "is_pleasant": True,
            "linked_habit": self.linked_habit_pleasant.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("У приятной привычки не может быть вознаграждения или связанной привычки", str(response.data))

    def test_linked_habit_not_pleasant(self):
        url = reverse('habit-list-create')
        data = {
            "location": "Дом",
            "time": "08:00:00",
            "action": "Утренняя йога",
            "duration": 30,
            "is_public": True,
            "is_pleasant": False,
            "linked_habit": self.linked_habit_not_pleasant.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("В связанные привычки могут попадать только привычки с признаком приятной привычки",
                      str(response.data))

    def test_habit_frequency_validation(self):
        url = reverse('habit-list-create')
        data = {
            "location": "Дом",
            "time": "08:00:00",
            "action": "Утренняя пробежка",
            "duration": 20,
            "is_public": True,
            "frequency": 8
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Нельзя выполнять привычку реже, чем 1 раз в 7 дней", str(response.data))

    def test_get_public_habits(self):
        Habit.objects.create(user=self.user, location="Дом", time="07:00:00",
                             action="Чтение", duration=30, is_public=True)
        Habit.objects.create(user=self.other_user, location="Парк", time="08:00:00",
                             action="Бег", duration=20, is_public=True)
        Habit.objects.create(user=self.other_user, location="Офис", time="09:00:00",
                             action="Работа", duration=60, is_public=False)
        url = reverse('public-habit-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)  # Только 4 публичные привычки

        # Проверка, что привычки принадлежат разным пользователям
        habit_user_emails = set(habit['user'] for habit in response.data['results'])
        self.assertEqual(len(habit_user_emails), 2)

class TestTelegramIntegration(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email='test@example.com', password='testpass123')
        self.habit = Habit.objects.create(
            user=self.user,
            location="Дом",
            time=timezone.now().time(),
            action="Чтение",
            frequency=1
        )
        self.habit_due_soon = Habit.objects.create(
            user=self.user,
            location="Дом",
            time=(timezone.now() + timedelta(minutes=5)).time(),
            action="Утренняя пробежка",
            frequency=1
        )

        self.habit_not_due_soon = Habit.objects.create(
            user=self.user,
            location="Дом",
            time=(timezone.now() + timedelta(hours=2)).time(),
            action="Вечерняя йога",
            frequency=1
        )
        self.chat_id = '123456789'
        TelegramUser.objects.create(user=self.user, chat_id=self.chat_id, is_account_linked=True)

    @mock.patch('habit.telegram_utils.requests.post')
    def test_send_telegram_message(self, mock_post):
        mock_post.return_value.ok = True
        chat_id = '123456'
        message = 'Test Message'
        bot_token = 'test_token'

        success = send_telegram_message(chat_id, message, bot_token)

        self.assertTrue(success)
        mock_post.assert_called_once_with(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )

    @mock.patch('habit.telegram_utils.requests.get')
    @mock.patch('habit.telegram_utils.requests.post')
    def test_get_updates(self, mock_post, mock_get):
        mock_response = {
            "ok": True,
            "result": [
                {"update_id": 1, "message": {"chat": {"id": "chat_id"}, "text": "test@example.com"}}
            ]
        }
        mock_get.return_value.json.return_value = mock_response

        mock_post.return_value.ok = True

        user = self.user

        get_updates('test_token')

        telegram_user = TelegramUser.objects.get(chat_id="chat_id")
        self.assertEqual(telegram_user.user, user)

        mock_post.assert_called_with(
            f"https://api.telegram.org/bottest_token/sendMessage",
            json={"chat_id": "chat_id", "text": "Ваш аккаунт успешно связан с Telegram."}
        )

    def test_get_due_habits(self):
        due_habits = get_due_habits()
        self.assertIn(self.habit_due_soon, due_habits)
        self.assertNotIn(self.habit_not_due_soon, due_habits)

    def test_record_habit_completion(self):
        record_habit_completion(self.habit)

        completion = HabitCompletion.objects.filter(habit=self.habit).first()
        self.assertIsNotNone(completion)
        self.assertEqual(completion.habit, self.habit)
        self.assertEqual(completion.completion_date, timezone.now().date())

    @mock.patch('habit.tasks.send_telegram_message')
    @mock.patch('habit.tasks.get_due_habits')
    def test_check_and_send_reminders(self, mock_get_due_habits, mock_send_telegram_message):
        mock_get_due_habits.return_value = [self.habit]
        mock_send_telegram_message.return_value = True

        check_and_send_reminders()

        mock_get_due_habits.assert_called_once()
        mock_send_telegram_message.assert_called_once_with('123456789',
                                                           f"Напоминание: Чтение в Дом в {self.habit.time.strftime('%H:%M')}",
                                                           mock.ANY)

        self.assertEqual(self.habit.completions.count(), 1)

    def tearDown(self):
        # Очистка после тестов
        self.user.delete()
        self.habit.delete()