from django.contrib.auth import get_user_model
from django.db.models import F, Q, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet
from recipe.models import (Carts, Favorites, Ingredient,
                           Recipe, Tag)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscriptions

from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import IsAdminOrReadOnly, IsAuthorStaffOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserRecipeSerializer,
                          UserSubscribeSerializer)

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorStaffOrReadOnly, )
    pagination_class = PageLimitPagination

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        if not self.request.user.is_anonymous:
            is_in_cart = self.request.query_params.get('is_in_shopping_cart')
            if is_in_cart in ['0', 'false']:
                queryset = queryset.filter(in_carts__user=self.request.user)
            elif is_in_cart in ['1', 'true']:
                queryset = queryset.exclude(in_carts__user=self.request.user)

            is_favorited = self.request.query_params.get('is_favorited')
            if is_favorited in ['1', 'true']:
                queryset = queryset.filter(in_favorites__user=self.
                                           request.user)
            elif is_favorited in ['0', 'false']:
                queryset = queryset.exclude(in_favorites__user=self.
                                            request.user)

        return queryset

    def list(self, request, *args, **kwargs):
        self.serializer_class = UserRecipeSerializer
        return super().list(request, *args, **kwargs)

    @action(methods=['GET', 'POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self._add_del_obj(pk, Favorites, Q(recipe__id=pk))

    @action(
        methods=['GET', 'POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        return self._add_del_obj(pk, Carts, Q(recipe__id=pk))

    @action(methods=['GET'], detail=False)
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.carts.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = []

        ingredients = Ingredient.objects.filter(
            recipe__in_carts__user=user
        ).values(
            'name',
            measurement=F('measurement_unit')
        ).annotate(amount=Sum('recipe__amount'))

        for ing in ingredients:
            shopping_list.append(
                f'{ing["name"]}: {ing["amount"]} {ing["measurement"]}'
            )

        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class UserViewSet(UserViewSet, AddDelViewMixin):
    pagination_class = PageLimitPagination
    add_serializer = UserSubscribeSerializer
    permission_classes = (IsAuthenticated, )

    @action(
        methods=['GET', 'POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id):
        return self._add_del_obj(id, Subscriptions, Q(author__id=id))

    @action(methods=['GET', ],
            detail=False)
    def subscriptions(self, request):
        if self.request.user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        pages = self.paginate_queryset(
            User.objects.filter(subscribers__user=self.request.user)
        )
        serializer = UserSubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)
