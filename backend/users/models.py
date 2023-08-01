from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Модель пользователя приложения Foodgram.
    """
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=100,
        unique=True,
    )
    username = models.CharField(
        verbose_name='username',
        max_length=100,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=100,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
    )
    is_active = models.BooleanField(
        verbose_name='Активирован',
        default=True,
    )
    is_admin = models.BooleanField(
        verbose_name='Администратор',
        default=False
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscriptions(models.Model):
    """
    Подписки пользователей.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscribers',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчики',
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        ordering = ('-date_added', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписаться на самого себя'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
