import os
import sys
import django
from .telegram_utils import send_telegram_message

sys.path.append('C:/Users/ASUS/PycharmProjects/atomic_habbits')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APITestCase
from users.models import CustomUser
from .models import Habit, TelegramUser
from django.urls import reverse
from rest_framework import status


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

        #проверка метода __str__
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
