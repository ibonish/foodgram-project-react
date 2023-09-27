from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import CONSTANTS


class User(AbstractUser):
    email = models.EmailField(verbose_name='Почта',
                              max_length=CONSTANTS['EMAIL'],
                              unique=True)
    username = models.CharField(unique=True,
                                max_length=CONSTANTS['MAX_1'],
                                verbose_name='Ник')
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=CONSTANTS['MAX_1'])
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=CONSTANTS['MAX_1'])
    password = models.CharField(verbose_name='Пароль',
                                max_length=CONSTANTS['MAX_1'])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Ник: {self.username}\nПочта: {self.email}'


class Subscriptions(models.Model):
    author = models.ForeignKey(User,
                               related_name='subscribers',
                               on_delete=models.CASCADE,
                               verbose_name='Автор')
    user = models.ForeignKey(User,
                             related_name='subscriptions',
                             on_delete=models.CASCADE,
                             verbose_name='Подписчик')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписаться на самого себя'
            )
        ]
        ordering = ('author', )
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на самого себя')

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
