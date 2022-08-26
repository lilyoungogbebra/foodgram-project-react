from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import CustomRecipeFilterSet, IngredientSearchFilter
from .mixins import ListRetrieveModelViewSet
from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     ShoppingUserList, Tag)
from .pagination import RecipePagination
from .permissions import AdminAllOnlyAuthorPermission
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer)


def post_delete_relationship_user_with_object(
        request,
        pk,
        model,
        message):
    recipe = get_object_or_404(Recipe, id=pk)
    if request.method == 'POST':
        if model.objects.filter(
                recipe=recipe,
                user=request.user).exists():
            return Response(
                {'errors': f'Рецепт под номером {pk} уже у вас в {message}.'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(
            recipe=recipe,
            user=request.user
        )
        serializer = RecipeSerializer()
        return Response(serializer.to_representation(instance=recipe),
                        status=status.HTTP_201_CREATED)
    obj_recipe = model.objects.filter(
        recipe=recipe,
        user=request.user
    )
    if obj_recipe.exists():
        obj_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'errors': f'Рецепта под номером {pk} у вас нет {message}.'},
        status=status.HTTP_400_BAD_REQUEST
    )


class RecipeViewSet(viewsets.ModelViewSet):
    '''Вьюсет рецептов.'''
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CustomRecipeFilterSet
    permission_classes = (
        permissions.IsAuthenticated,
        AdminAllOnlyAuthorPermission,
    )

    def get_permissions(self):
        '''Ветвление пермишенов.'''
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        '''При создании или обновлении рецепта, выбираем другой сериализатор'''
        if self.action in ['create', 'partial_update', 'update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        '''Эндпоинт для избранных рецептов.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=FavoritesRecipesUserList,
            message='избранном'
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        '''Эндпоинт для списка покупок.'''
        return post_delete_relationship_user_with_object(
            request=request,
            pk=pk,
            model=ShoppingUserList,
            message='списке покупок'
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        '''Эндпоинт для загрузки списка покупок.'''
        recipes_user_in_shoplist = ShoppingUserList.objects.filter(
            user=request.user
        )
        recipes = Recipe.objects.filter(
            recipe_in_shoplist__in=recipes_user_in_shoplist
        )
        ingredients = Ingredient.objects.filter(
            ingredient_in_recipe__recipe__in=recipes
        )
        queryset_ingredients = ingredients.annotate(
            sum_amount_ingredients=(Sum('ingredient_in_recipe__amount'))
        )
        content = (
            'Ваш сервис, продуктовый помощник, подготовил \n список '
            + 'покупок по выбранным рецептам:\n'
            + 50 * '_'
            + '\n\n'
        )
        if not queryset_ingredients:
            content += (
                'К сожалению, в списке ваших покупок пусто - '
                + 'так как вы не добавили в него ни одного рецепта.'
            )
        else:
            for ingr in queryset_ingredients:
                content += (
                    f'\t•\t{ingr.name} ({ingr.measurement_unit}) — '
                    + f'{ingr.sum_amount_ingredients}\n\n'
                )
        filename = 'my_shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(
            filename
        )
        return response


class TagViewSet(ListRetrieveModelViewSet):
    '''Вьюсет для тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveModelViewSet):
    '''Вьюсет для ингредиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
