from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Carts, Favorite, Ingridients, Recipes, Tags
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscriptions, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthenticatedAuthorOrReadOnly
from .serializers import (CCRecipeSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShortRecipesSerializer, SubscriptionsSerializer,
                          TagSerializer)


class LimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'
    page_size = 5
    max_page_size = 100


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


class СustomUserViewSet(UserViewSet):
    """
    Вьюсет для пользователей foodgram (переопределение стандартного в joser).
    Эндпоинты:
        * api/users/
        * api/users/{id}/
        * api/users/me/
        * api/users/set_password/
        * api/users/{id}/subscribe/
        * api/users/subscriptions/
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated, )
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        self.serializer_class = CustomUserSerializer
        return super().list(request, *args, **kwargs)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        from_user = request.user
        to_user = get_object_or_404(User, id=id)

        if from_user == to_user:
            return Response(
                {'error':
                 'Невозможно подписаться/отменить подписку на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if Subscriptions.objects.filter(author=to_user,
                                            user=from_user).exists():
                return Response(
                    {'error': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            sub = Subscriptions.objects.create(
                user=from_user,
                author=to_user
            )
            sub.save()
            serializer = SubscriptionsSerializer(
                to_user,
                many=False,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Subscriptions.objects.filter(author=to_user,
                                                user=from_user).exists():
                return Response(
                    {'error': 'Вы не подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.filter(
                user=from_user,
                author=to_user
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET', ],
            permission_classes=(IsAuthenticated, ),
            detail=False,
            )
    def subscriptions(self, request):
        authors = User.objects.filter(
            subscribers__user=request.user
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
    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    permission_classes = (IsAuthenticatedAuthorOrReadOnly, )
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('^ingredients__name', )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return CCRecipeSerializer

    @action(methods=['POST', 'DELETE'],
            detail=True,)
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        favorite = Favorite.objects.filter(user=user,
                                           recipe=recipe)

        if self.request.method == 'POST':
            if favorite.exists():
                return Response({'error': 'Рецепт уже добавлен в избранное'},
                                status=status.HTTP_400_BAD_REQUEST)
            new_fav = Favorite.objects.create(user=user,
                                              recipe=recipe)
            new_fav.save()
            serializer = ShortRecipesSerializer(
                recipe,
                many=False,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipes, pk=pk)
        cart = Carts.objects.filter(user=user,
                                    recipe=recipe)

        if self.request.method == 'POST':
            if cart.exists():
                return Response({'error': 'Рецепт уже добавлен в корзину'},
                                status=status.HTTP_400_BAD_REQUEST)
            new_cart = Carts.objects.create(user=user,
                                            recipe=recipe)
            new_cart.save()
            serializer = ShortRecipesSerializer(
                recipe,
                many=False,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if cart.exists():
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Рецепта не существует'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET', ],
            detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        carts = Carts.objects.filter(user=user)
        final_list = ''
        for cart in carts:
            recipe = cart.recipe
            ingredients_used = recipe.ingredients_used.all()
            for ing in ingredients_used:
                ingredient_name = ing.ingredients.name
                measurement_unit = ing.ingredients.measurement_unit
                amount = ing.amount
                final_list += f"{ingredient_name} - {amount} ({measurement_unit})\n"
        response = HttpResponse(final_list, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response
