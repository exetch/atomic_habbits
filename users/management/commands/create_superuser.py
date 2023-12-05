from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Create a specific superuser with email and password.'

    def handle(self, *args, **options):
        user = CustomUser.objects.create(
            email='example@admina.net',
            first_name='admin',
            last_name='adminov',
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        user.set_password('123qwe456rty')
        user.save()
