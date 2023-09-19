import django_filters
from recipes.models import Recipes
from django_filters.rest_framework import FilterSet, filters
from recipes.models import Tags, Ingridients


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')
    
    class Meta:
        model = Ingridients
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """
    Фильрация по для рецепта.
    """
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )

    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    author = django_filters.NumberFilter(
        field_name='author',
        method='filter_author'
    )

    # tags = django_filters.CharFilter(
    #     field_name='tags__slug',
    #     method='filter_tags',
    #     lookup_expr='in'
    # )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all(),
    )

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            if not user.is_anonymous:
                return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            if not user.is_anonymous:
                return queryset.filter(carts__user=user)
        return queryset

    def filter_author(self, queryset, name, value):
        return queryset.filter(author=value)

    # def filter_tags(self, queryset, name, value):
    #     tags = value.split('&')
    #     return queryset.filter(tags__slug__in=tags)

    class Meta:
        model = Recipes
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
