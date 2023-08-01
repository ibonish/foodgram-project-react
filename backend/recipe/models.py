from django.contrib.auth import get_user_model
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель отдельного ингридиента с единицой измерения.
    Связана с моделью Recipe через модель AmountIngridients.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=20
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """
    Тэг рецепта, связан с моделью Recipe.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Поле должно содержать HEX-код цвета'
            )
        ]
    )
    slug = models.SlugField(
        verbose_name='Cлаг',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Recipe(models.Model):
    """
    Модель рецепта.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='images/'
    )
    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='AmountIngridients',
        through_fields=('recipe', 'ingredients'),
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class AmountIngridients(models.Model):
    """
    Количество ингридиентов.
    Связывает модель Ingredient c Recipe
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты с данным ингридиентом',
        on_delete=models.CASCADE,
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'

    def __str__(self) -> str:
        return f'{self.ingredients} - {self.amount}'


class Favorites(models.Model):
    """
    Избранные рецепты.
    Модель связывает Recipe c User.
    """

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранные рецепты',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Carts(models.Model):
    """
    Рецепты в корзине покупок.
    Модель связывает Recipe и User.
    """
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='carts',
        on_delete=models.CASCADE,
    )
    date_added = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'
