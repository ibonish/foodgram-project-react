from django.http import FileResponse
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from recipes.models import (
    AmountIngridients, Carts, Favorite, Ingridients, Recipes, Tags
)
from users.models import Subscriptions, User
from .filters import IngredientFilter, RecipeFilter
from .paginators import LimitPagination
from .permissions import IsAuthenticatedAuthorOrReadOnly
from .serializers import (
    CreateSubscriptionsSerializer,
    CreateUpdateRecipeSerializer,
    FoodgramUserSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    FavoriteSerializer,
    CartsSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Отображение тэгов.
    Эндпоинты:
        * api/tags/
        * api/tags/{id}/
    """
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )


class IngridientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Отображение списка ингредиентов с возможностью поиска по имени.
    Эндпоинты:
        * api/ingredients/
        * api/ingredients/{id}/
    """
    queryset = Ingridients.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ['name']


class FoodgramUserViewSet(UserViewSet):
    """
    Вьюсет для пользователей foodgram (переопределение стандартного в djoser).
    Эндпоинты:
        * api/users/
        * api/users/{id}/
        * api/users/me/
        * api/users/set_password/
        * api/users/{id}/subscribe/
        * api/users/subscriptions/
    """
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated, )
        return super().get_permissions()

    @action(
        methods=['POST', ],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        from_user = request.user.id
        data = {
            'user': from_user,
            'author': id
        }
        serializer = CreateSubscriptionsSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        from_user = request.user
        subscription = Subscriptions.objects.filter(author_id=id,
                                                    user=from_user)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['GET', ],
            permission_classes=(IsAuthenticated, ),
            detail=False,
            )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscriptions__user=request.user
        )
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionsSerializer(
            authors,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.select_related('author').prefetch_related(
        'ingredients',
        'tags'
    )
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticatedAuthorOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('^ingredients__name', )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return CreateUpdateRecipeSerializer

    @staticmethod
    def create_relation(request, serializer_class, pk):
        user = request.user.id
        data = {'user': user,
                'recipe': pk}
        serializer = serializer_class(data=data,
                                      context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_relation(request, pk, model):
        user = request.user
        object = model.objects.filter(user=user,
                                      recipe_id=pk)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Рецепт не добавлен'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', ],
            detail=True,)
    def favorite(self, request, pk):
        return self.create_relation(request, FavoriteSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_relation(request, pk, Favorite)

    @action(methods=['POST', ],
            detail=True)
    def shopping_cart(self, request, pk):
        return self.create_relation(request, CartsSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_relation(request, pk, Carts)

    @staticmethod
    def get_file_response(queryset):
        final_list = ''
        for ingredient in queryset:
            ingredient_name = ingredient['ingredients__name']
            measurement_unit = ingredient['ingredients__measurement_unit']
            amount = ingredient['amount']
            final_list += (
                f'{ingredient_name} - {amount} ({measurement_unit})\n'
            )

        response = FileResponse(open('shopping_cart.txt', 'rb'))
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_cart.txt"'
        return response

    @action(methods=['GET', ],
            detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_used = AmountIngridients.objects.filter(
            recipe__carts__user=user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by('ingredients__name')
        return self.get_file_response(ingredients_used)
