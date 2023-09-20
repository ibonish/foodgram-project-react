from django.contrib.admin import ModelAdmin, TabularInline, register
from import_export.admin import ImportExportModelAdmin

from .models import (AmountIngridients, Carts, Favorite, Ingridients, Recipes,
                     Tags)


class IngredientInline(TabularInline):
    model = AmountIngridients


@register(AmountIngridients)
class AmountIngridientsAdmin(ModelAdmin):
    list_display = (
        'recipe', 'ingredients', 'amount'
    )


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe',
    )


@register(Ingridients)
class IngredientAdmin(ImportExportModelAdmin):
    pass


@register(Recipes)
class RecipeAdmin(ModelAdmin):
    inlines = (IngredientInline, )
    list_display = (
        'name', 'author',
    )
    fields = (
        ('name', ),
        ('cooking_time', ),
        ('author', ),
        ('tags', ),
        ('text',),
        ('image',),
    )


@register(Tags)
class TagAdmin(ModelAdmin):
    list_display = (
        'name', 'slug', 'color',
    )


@register(Carts)
class CardAdmin(ModelAdmin):
    list_display = (
        'user', 'recipe',
    )
