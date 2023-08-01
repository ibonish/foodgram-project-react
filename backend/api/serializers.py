from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import F
from recipe.models import AmountIngridients, Ingredient, Recipe, Tag
from rest_framework.fields import ImageField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, obj):
        """
        Проверка подписки пользователей.
        """
        user = self.context.get('request').user

        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def create(self, validated_data):
        """
        Создаёт нового пользователя.
        """
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели Recipe, для отображения в подписках.
    """

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = ('__all__',)


class UserSubscribeSerializer(UserSerializer):
    recipes = UserRecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('__all__',)

    def get_is_subscribed(self, obj):
        """
        Проверка подписки пользователей.
        """
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscriptions.filter(author=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__', )


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)

    def validate(self, data):
        for key, value in data.items():
            data[key] = value.sttrip(' #').upper()
        return data


class RecipeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit',
            amount=F('amountingridients__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.carts.filter(recipe=recipe).exists()

    def validate(self, data):
        tags_ids = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not tags_ids or not ingredients:
            raise ValidationError('Недостаточно данных')

        if not tags_ids:
            raise ValidationError('Добавьте тэги')

        tags = Tag.objects.filter(id__in=tags_ids)

        if len(tags) != len(tags_ids):
            raise ValidationError('Несуществующий тэг')

        if not ingredients:
            raise ValidationError('Укажите ингридиенты')

        validated_ings = {}

        for ing in ingredients:
            if not (isinstance(ing['amount'], int) or ing['amount'].isdigit()):
                raise ValidationError('Неправильное количество ингидиента')

            validated_ings[ing['id']] = int(ing['amount'])
            if validated_ings[ing['id']] <= 0:
                raise ValidationError('Неправильное количество ингридиента')

        if not validated_ings:
            raise ValidationError('Неправильные ингидиенты')

        db_ings = Ingredient.objects.filter(pk__in=validated_ings.keys())
        if not db_ings:
            raise ValidationError('Неправильные ингидиенты')

        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        objs = []
        for ingredient, amount in ingredients.values():
            objs.append(
                AmountIngridients(
                    recipe=recipe, ingredients=ingredient, amount=amount
                )
            )
        AmountIngridients.objects.bulk_create(objs)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        for key, value in validated_data.items():
            if hasattr(recipe, key):
                setattr(recipe, key, value)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            objs = []
            for ingredient, amount in ingredients.values():
                objs.append(
                    AmountIngridients(
                        recipe=recipe, ingredients=ingredient, amount=amount
                    )
                )
        AmountIngridients.objects.bulk_create(objs)
        recipe.save()
        return recipe
