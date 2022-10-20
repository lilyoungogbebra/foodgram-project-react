import django_filters as filters

from .models import Ingredient, Recipe, Tag


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтрсет рецептов."""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value == 1:
            return queryset.filter(favorite__user=self.request.user)
        if value == 0:
            return queryset.exclude(favorite__user=self.request.user)
        return queryset.none()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset
        if value == 1:
            return queryset.filter(shoppinglist__user=self.request.user)
        if value == 0:
            return queryset.exclude(shoppinglist__user=self.request.user)
        return queryset.none()

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)
