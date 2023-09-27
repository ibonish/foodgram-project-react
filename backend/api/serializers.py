from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer
from rest_framework import serializers

from foodgram.settings import CONSTANTS
from users.models import Subscriptions, User
from recipes.models import (
    AmountIngridients,
    Carts,
    Favorite,
    Ingridients,
    Recipes,
    Tags,
)


class FoodgramUserSerializer(UserSerializer):
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
        user = self.context['request'].user
        return user.is_authenticated and Subscriptions.objects.filter(
            user=user, author=obj.id).exists()


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

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(FoodgramUserSerializer):
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
        recipe_list = obj.recipes_user.all()
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            recipe_list = recipe_list[:int(limit)]
        return ShortRecipesSerializer(recipe_list, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes_user.count()


class CreateSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ('user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']
        object = Subscriptions.objects.filter(user=user,
                                              author=author)
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя')
        if object.exists():
            raise serializers.ValidationError('Вы уже подписаны')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SubscriptionsSerializer(instance.author, context=context).data


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


class GetAmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='ingredients.id',
        read_only=True
    )
    name = serializers.CharField(
        source='ingredients.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit',
        read_only=True
    )

    class Meta:
        model = AmountIngridients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class PostAmountIngredientSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingridients.objects.all(),
                                            many=False)
    amount = serializers.IntegerField(min_value=CONSTANTS['MIN_VAL'],
                                      max_value=CONSTANTS['MAX_VAL_AMOUNT'],)

    class Meta:
        model = AmountIngridients
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения списка рецептов.
    """
    ingredients = GetAmountIngredientSerializer(source='ingredients_used',
                                                many=True)
    tags = TagSerializer(many=True, read_only=True)
    author = FoodgramUserSerializer()
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
        return user.is_authenticated and Favorite.objects.filter(
            user=user, recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        return user.is_authenticated and Carts.objects.filter(
            user=user, recipe=object).exists()


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.
    """
    ingredients = PostAmountIngredientSerializer(many=True,
                                                 source='ingredients_used')
    tags = serializers.PrimaryKeyRelatedField(queryset=Tags.objects.all(),
                                              many=True)
    author = FoodgramUserSerializer(read_only=True, )
    image = Base64ImageField()

    class Meta:
        model = Recipes
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'name',
                  'image',
                  'text',
                  'cooking_time')

    @staticmethod
    def process_ingredients(ingredients, instance):
        ingredients_to_create = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            ingredients_to_create.append(AmountIngridients(
                recipe=instance,
                ingredients=ingredient_id,
                amount=amount
            ))
        AmountIngridients.objects.bulk_create(ingredients_to_create)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        user = self.context['request'].user
        recipe = Recipes.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.process_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        new_ingredients = validated_data.pop('ingredients_used')
        new_tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(new_tags)
        AmountIngridients.objects.filter(recipe_id=instance.pk).delete()
        self.process_ingredients(new_ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        object = self.Meta.model.objects.filter(user=user,
                                                recipe=recipe)
        if object.exists():
            raise serializers.ValidationError('Рецепт уже добавлен')
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipesSerializer(instance.recipe, context=context).data


class CartsSerializer(FavoriteSerializer):
    class Meta:
        model = Carts
        fields = '__all__'
