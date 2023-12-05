from random import choice
from django.core.management.base import BaseCommand
from faker import Faker
from habit.models import Habit
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Создает двух тестовых пользователей'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(2):
            email = fake.email()
            password = '123qwe456rty'
            first_name = fake.first_name()
            last_name = fake.last_name()
            phone_number = fake.numerify(text='###########')
            country = fake.country()

            user = CustomUser.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                country=country,
                is_superuser=False,
                is_staff=False,
                is_active=True
            )
            user.set_password(password)
            self.stdout.write(f'Создан пользователь {email}')
            user.save()

            self.create_habits_for_user(user)

    def create_habits_for_user(self, user):
        fake = Faker()
        for _ in range(10):
            ACTIONS = [
                "Заниматься йогой",
                "Читать книгу",
                "Прогулка на свежем воздухе",
                "Медитация",
                "Учить новый язык",
                "Практиковать гитару",
                "Писать дневник",
                "Ранняя зарядка",
                "Здоровое питание",
                "Учиться программированию"
            ]

            REWARDS = [
                "Смотреть любимый сериал",
                "Играть в видеоигры",
                "Лакомство",
                "Кофе в любимой кофейне",
                "Поход в кино",
                "Время для хобби",
                "Прогулка в парке",
                "Спа-процедуры",
                "Встреча с друзьями",
                "Расслабляющая ванна"
            ]
            habit = Habit.objects.create(
                user=user,
                location=fake.city(),
                time=fake.time(),
                action=choice(ACTIONS),
                is_pleasant=fake.boolean(),
                linked_habit=None,
                frequency=fake.random_int(min=1, max=7),
                reward=choice(REWARDS) if fake.boolean() else '',
                duration=fake.random_int(min=1, max=120),
                is_public=fake.boolean()
            )
            self.stdout.write(f'Создана привычка {habit.action} для пользователя {user.email}')


{
    "location": "дома",
    "time": "10:00",
    "action": "Писать книгу",
    "is_pleasant": "false",
    "linked_habit": 33,
    "frequency": 1,
    "reward": "маффин",
    "duration": 100,
    "is_public": "true"

}
