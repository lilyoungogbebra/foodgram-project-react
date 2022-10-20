from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientNameFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, Tag
from .paginators import CustomPageNumberPaginator
from .permissions import IsRecipeOwnerOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerialiser,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer)

User = get_user_model()


class ListRetrieveModelViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    '''
    Кастомный базовый вьюсет:
    Вернуть список объектов (GET);
    Вернуть объект (GET);
    '''
    pass


class FavoriteAndCartMixin:
    def favorite_and_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeWriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(
            Favorite, user=request.user.id, recipe__id=pk
        )
        favorite.delete()
        return Response(
            f'Рецепт {recipe.name} - удален',
            status=status.HTTP_204_NO_CONTENT,
        )


class TagViewSet(ListRetrieveModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerialiser
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_class = IngredientNameFilter


class RecipeViewSet(viewsets.ModelViewSet, FavoriteAndCartMixin):
    queryset = Recipe.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = (IsRecipeOwnerOrReadOnly,)
    pagination_class = CustomPageNumberPaginator
    filterset_fields = (
        'tags',
        'author',
        'is_favorited',
        'is_in_shopping_cart'
    )

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(
        methods=['GET'],
        detail=False,
        url_name='download_shopping_cart',
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = self.request.user
        recipes = user.shoppingcart.all().values_list('recipe', flat=True)
        ingredients = recipes.values(
            'ingredients__name',
            'ingredients__measurement_unit__name').order_by(
            'ingredients__name').annotate(
            ingredients_total=Sum('ingredient_amounts__amount')
        )
        buying = {}
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            amount = ingredient.amount
            unit = ingredient.ingredient.measurement_unit
            if name not in buying:
                buying[name] = {'amount': amount, 'unit': unit}
            else:
                buying[name]['amount'] = (
                    buying[name]['amount'] + amount
                )
        shopping_list = []
        for item in buying:
            shopping_list.append(
                f'{item} - {buying[item]["amount"]}, '
                f'{buying[item]["unit"]}\n'
            )
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment;' 'filename="shopping_list.txt"'
        )
        return response


class ShoppingCartView(viewsets.ModelViewSet, FavoriteAndCartMixin):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'delete']
