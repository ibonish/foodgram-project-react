from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.utils.html import format_html

User = get_user_model()


class Tags(models.Model):
    name = models.CharField(max_length=20)
    color = models.CharField(max_length=7,
                             default="#ffffff",
                             validators=[RegexValidator()])
    slug = models.SlugField(max_length=20)

    def colored_name(self):
        return format_html(
            '<span style="color: #{};">{}</span>',
            self.color,
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Ingridients(models.Model):
    name = models.CharField(max_length=100)
    measurement_unit = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipes(models.Model):
    tags = models.ManyToManyField(Tags,
                                  related_name='recipes_tags')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes_user')
    ingredients = models.ManyToManyField(Ingridients,
                                         through='AmountIngridients',
                                         through_fields=('recipe',
                                                         'ingredients'),
                                         related_name='recipes_ingredients'
                                         )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class AmountIngridients(models.Model):
    recipe = models.ForeignKey(Recipes,
                               related_name='ingredients_used',
                               on_delete=models.CASCADE)
    ingredients = models.ForeignKey(Ingridients,
                                    related_name='recipe_used',
                                    on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1),
                    MaxValueValidator(1000)]
    )

    class Meta:
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.ingredients} - {self.amount}'


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite_recipes',
                # violation_error_message='рецепт уже добавлен в избранное'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class Carts(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    user = models.ForeignKey(User,
                             related_name='carts',
                             on_delete=models.CASCADE,
                             )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_favorite_carts',
                # violation_error_message='рецепт уже добавлен в корзину'
            ),
        )
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'
