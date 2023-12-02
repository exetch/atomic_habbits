from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    email_verificated = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, verbose_name='Имя', null=True, blank=True)
    last_name = models.CharField(max_length=30, verbose_name='Фамилия', null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

