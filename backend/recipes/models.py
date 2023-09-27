from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,)
from django.db import models
from colorfield.fields import ColorField

from foodgram.settings import CONSTANTS
from users.models import User


class Tags(models.Model):
    name = models.CharField(max_length=CONSTANTS['MAX_2'],
                            verbose_name='Тег')
    color = ColorField(default='#FF0000',
                       verbose_name='Цвет')
    slug = models.SlugField(max_length=CONSTANTS['MAX_2'],
                            verbose_name='Слаг')

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Ingridients(models.Model):
    name = models.CharField(max_length=CONSTANTS['MAX_2'],
                            verbose_name='Ингредиент')
    measurement_unit = models.CharField(max_length=CONSTANTS['MAX_2'],
                                        verbose_name='Единица измерения')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            ),
        )
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipes(models.Model):
    tags = models.ManyToManyField(Tags,
                                  related_name='recipes_tags',
                                  verbose_name='Тэги')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes_user',
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(Ingridients,
                                         through='AmountIngridients',
                                         through_fields=('recipe',
                                                         'ingredients'),
                                         related_name='recipes_ingredients',
                                         verbose_name='Ингредиенты'
                                         )
    name = models.CharField(max_length=CONSTANTS['MAX_2'],
                            verbose_name='Название')
    image = models.ImageField(upload_to='images/',
                              verbose_name='Картинка')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(CONSTANTS['MIN_VAL']),
                    MaxValueValidator(CONSTANTS['MAX_VAL_COOK'])]
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации')

    class Meta:
        ordering = ('pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class AmountIngridients(models.Model):
    recipe = models.ForeignKey(Recipes,
                               related_name='ingredients_used',
                               on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingridients,
                                    related_name='recipe_used',
                                    on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(CONSTANTS['MIN_VAL']),
                    MaxValueValidator(CONSTANTS['MAX_VAL_AMOUNT'])]
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredients} - {self.amount}'


class AbstractUserRecipeRelation(models.Model):
    recipe = models.ForeignKey(Recipes,
                               on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил в {self._meta.verbose_name} {self.recipe}'


class Favorite(AbstractUserRecipeRelation):
    class Meta:
        default_related_name = 'favorite'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite',
            ),
        ]


class Carts(AbstractUserRecipeRelation):
    class Meta:
        default_related_name = 'carts'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_cart',
            ),
        ]
