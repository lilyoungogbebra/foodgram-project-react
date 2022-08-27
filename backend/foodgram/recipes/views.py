from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action

from .filters import CustomRecipeFilterSet, IngredientSearchFilter
from .mixins import ListRetrieveModelViewSet
from .utils import post_delete_relationship_user_with_object
from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     ShoppingUserList, Tag)
from .pagination import RecipePagination
from .permissions import AdminAllOnlyAuthorPermission
from .serializers import (IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeSerializer, TagSerializer)


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
