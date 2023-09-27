from django.contrib.admin import ModelAdmin, TabularInline, register
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from .models import (AmountIngridients, Carts, Favorite, Ingridients, Recipes,
                     Tags)


class IngredientInline(TabularInline):
    model = AmountIngridients
    min_num = 1
    extra = 3


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
        'name', 'author', 'tags_list', 'ingredient_list', 'cooking_time'
    )
    fields = (
        ('name', ),
        ('cooking_time', ),
        ('author', ),
        ('tags', ),
        ('text',),
        ('image',),
    )

    @admin.display(description='Избранное')
    def favorite(self, obj):
        return obj.favorite.count()

    @admin.display(description='Ингредиенты')
    def ingredient_list(self, obj):
        return ', '.join([ing.name for ing in obj.ingredients.all()])

    @admin.display(description='Изображение')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description='Тэги')
    def tags_list(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])


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


admin.site.unregister(Group)
