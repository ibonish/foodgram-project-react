from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngridientsViewSet, RecipeViewSet, TagViewSet,
                    FoodgramUserViewSet)

router = SimpleRouter()
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngridientsViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('users', FoodgramUserViewSet, 'users')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
