from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()
    username = models.CharField(unique=True,
                                max_length=50,
                                verbose_name='Ник'
                                )
    first_name = models.CharField(verbose_name='Имя',
                                  max_length=50
                                  )
    last_name = models.CharField(verbose_name='Фамилия',
                                 max_length=50
                                 )
    password = models.CharField(verbose_name='Пароль',
                                max_length=128,
                                )
    is_active = models.BooleanField(verbose_name='Активирован',
                                    default=True,
                                    )
    is_admin = models.BooleanField(verbose_name='Администратор',
                                   default=False
                                   )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Ник: {self.username}\nПочта: {self.email}'


class Subscriptions(models.Model):
    author = models.ForeignKey(User,
                               related_name='subscribers',
                               on_delete=models.CASCADE,
                               )
    user = models.ForeignKey(User,
                             related_name='subscriptions',
                             on_delete=models.CASCADE,
                             )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Нельзя подписаться на самого себя'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписался на {self.author.username}'
