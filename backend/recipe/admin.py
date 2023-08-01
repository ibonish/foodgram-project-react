from django.contrib.admin import ModelAdmin, register
from .models import (AmountIngridients,
                     Ingredient,
                     Recipe,
                     Tag,
                     Favorites,
                     Carts)
from .forms import TagForm


@register(AmountIngridients)
class LinksAdmin(ModelAdmin):
    pass


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = (
        'name',
    )
    list_filter = (
        'name',
    )


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name', 'author',
    )
    fields = (
        ('name', 'cooking_time',),
        ('author', 'tags',),
        ('text',),
        ('image',),
    )
    search_fields = (
        'name', 'author__username', 'tags__name',
    )
    list_filter = (
        'name', 'author__username', 'tags__name'
    )


@register(Tag)
class TagAdmin(ModelAdmin):
    form = TagForm
    list_display = (
        'name', 'slug', 'color',
    )
    search_fields = (
        'name', 'color'
    )


@register(Favorites)
class FavoriteAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe', 'date_added'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )


@register(Carts)
class CardAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe', 'date_added'
    )
    search_fields = (
        'user__username', 'recipe__name'
    )
