from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngridients, Carts, Favorite, Ingridients,
                            Recipes, Tags)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import Subscriptions, User


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для пользователей foodgram.
    Пример ответа:
        {
            "email": "user@example.com",
            "id": 0,
            "username": "string",
            "first_name": "Вася",
            "last_name": "Пупкин",
            "is_subscribed": false
        }
    Эндпоинты:
        * api/users/
        * api/users/{id}/
        * api/users/me/
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user,
                                            author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Регистрация пользователя foodgram.
    Переопределение дефолтного UserCreateSerializer в djoser.
    Пример ответа:
        {
            "email": "vpupkin@yandex.ru",
            "id": 0,
            "username": "vasya.pupkin",
            "first_name": "Вася",
            "last_name": "Пупкин"
        }
    Эндпоинты:
        * POST api/users/
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password')
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с указанным username'
            )
        return value


class ShortRecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения рецепта у пользователя и в избранном.
    Пример ответа:
    "recipes": [
        {
            "id": 0,
            "name": "string",
            "image": "http://foodgram.example.org/media/recipes/image.jpeg",
            "cooking_time": 1
        }
    ]
    """
    image = serializers.ImageField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения пользователей при подписке.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit is None:
            recipe_list = obj.recipes_user.all()
        else:
            recipe_list = obj.recipes_user.all()[:int(limit)]
        return ShortRecipesSerializer(recipe_list, many=True).data

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user,
                                            author=obj.id).exists()

    def get_recipes_count(self, obj):
        return obj.recipes_user.count()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения тегов.
    """
    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingridients
        fields = ('id', 'name', 'measurement_unit')


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredients.id',
    )
    name = serializers.CharField(
        source='ingredients.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
        read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = AmountIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка рецептов.
    """
    ingredients = AmountIngredientSerializer(source='ingredients_used',
                                             many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True, )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True, )

    class Meta:
        model = Recipes
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Carts.objects.filter(user=user, recipe=object).exists()


class CCRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.
    """
    ingredients = AmountIngredientSerializer(source='ingredients_used',
                                             many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    author = CustomUserSerializer(read_only=True, )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True, )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True, )

    class Meta:
        model = Recipes
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Carts.objects.filter(user=user).exists()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipes.objects.create(author=user, **validated_data)

        for tag in tags:
            recipe.tags.add(tag)

        for ing in ingredients:
            current_id = ing['ingredients']['id']
            current_amount = ing['amount']
            recipe.ingredients.add(
                current_id,
                through_defaults={
                    'amount': current_amount
                }
            )
        return recipe

    def update(self, instance, validated_data):
        new_ingredients = validated_data.pop('ingredients_used')
        new_tags = validated_data.pop('tags')
        instance.tags.clear()
        for tag in new_tags:
            instance.tags.add(tag)
        AmountIngridients.objects.filter(recipe_id=instance.pk).delete()

        for ing in new_ingredients:
            current_id = ing['ingredients']['id']
            current_amount = ing['amount']
            instance.ingredients.add(
                current_id,
                through_defaults={
                    'amount': current_amount
                }
            )
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data
