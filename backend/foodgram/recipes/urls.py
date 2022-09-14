from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, ShoppingCartView,
                    TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients'),
router.register('recipes', RecipeViewSet, basename='recipes'),

urlpatterns = [
    path(
        'recipes/<int:pk>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),
    path('', include(router.urls)),
]
