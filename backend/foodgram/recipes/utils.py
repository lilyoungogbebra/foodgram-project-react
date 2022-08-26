from rest_framework import serializers

from .models import Ingredient, RecipeIngredientRelationship


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
