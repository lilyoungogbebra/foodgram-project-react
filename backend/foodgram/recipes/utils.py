from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response

from .models import Ingredient, Recipe, RecipeIngredientRelationship
from .serializers import RecipeSerializer


def create_relationship_ingredient_recipe(ingredients, recipe):
    '''Наполнение связующей таблицы ингредиентами и рецептами.'''
    ingredient_list = []
    for ingredient in ingredients:
        cur_id = ingredient['id']
        current_ingredient = Ingredient.objects.filter(id=cur_id).first()
        if not current_ingredient:
            message = (
                f'Недопустимый первичный ключ \"{cur_id}\" -'
                + 'ингредиента не существует в нашей бд.'
            )
            raise serializers.is_valid(
                {'ingredients': [f'{message}']}
            )
        new_ingredient = RecipeIngredientRelationship(
            recipe=recipe,
            ingredient_id=cur_id,
            amount=ingredient['amount'],
        )
        ingredient_list.append(new_ingredient)
    RecipeIngredientRelationship.objects.bulk_create(ingredient_list)


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
