from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     RecipeIngredientRelationship, RecipeTagRelationship,
                     ShoppingUserList, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    '''Сериалайзер для тега.'''

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериалайзер для ингредиента.'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientRelationshipSerializer(serializers.ModelSerializer):
    '''Сериалайзер для таблицы Рецепта с ингредиентом.'''
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient.name')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredientRelationship
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериалайзер для рецепта.'''
    ingredients = RecipeIngredientRelationshipSerializer(
        read_only=True,
        many=True,
        source='ingredient_in_recipe'
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        '''Проверка, находится ли обьект в избранном.'''
        user = self.context['request'].user
        if (user != AnonymousUser()
                and FavoritesRecipesUserList.objects.filter(
                    user=user, recipe=obj.pk).exists()):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        '''Проверка, находится ли обьект в списке покупок.'''
        user = self.context['request'].user
        if (user != AnonymousUser()
                and ShoppingUserList.objects.filter(
                    user=user, recipe=obj.pk).exists()):
            return True
        return False


class RecipeIngredientAmountCreateUpdateSerializer(
        serializers.ModelSerializer):
    '''Сериалайзер для вывода кол-ва ингредиентов.'''
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredientRelationship
        fields = (
            'id',
            'amount',
        )


def create_relationship_tag_recipe(tags, recipe):
    '''Наполнение связующей таблицы тегами и рецептами.'''
    for tag in tags:
        RecipeTagRelationship.objects.create(tag=tag, recipe=recipe)


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
            raise serializers.ValidationError(
                {'ingredients': [f'{message}']}
            )
        new_ingredient = RecipeIngredientRelationship(
            recipe=recipe,
            ingredient_id=cur_id,
            amount=ingredient['amount'],
        )
        ingredient_list.append(new_ingredient)
    RecipeIngredientRelationship.objects.bulk_create(ingredient_list)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    '''Сериалайзер, производящий запись или обновление рецепта.'''
    ingredients = RecipeIngredientAmountCreateUpdateSerializer(
        many=True,
        source='ingredient_in_recipe'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        '''На вывод возвращаем рецепт через другой сериалайзер.'''
        return RecipeSerializer(instance, context=self.context).data

    def validate(self, data):
        '''Валидация на уровне объекта.'''
        if 'tags' in data:
            tags = data.get('tags')
            all_tags_request = len(tags)
            uniq_tags = set()
            for tag in tags:
                uniq_tags.add(tag.pk)
            if len(uniq_tags) != all_tags_request:
                raise serializers.ValidationError(
                    'теги должны быть уникальными.'
                )
        if 'ingredient_in_recipe' in data:
            ingredients = data.get('ingredient_in_recipe')
            all_ingredients_request = len(ingredients)
            uniq_ingredients = set()
            for ingredient in ingredients:
                id = ingredient['id']
                amount = ingredient['amount']
                if amount <= 0:
                    raise serializers.ValidationError(
                        'минимальное количество ингредиента: 1.'
                    )
                uniq_ingredients.add(id)
            if len(uniq_ingredients) != all_ingredients_request:
                raise serializers.ValidationError(
                    'Ингридиенты должны быть уникальными.'
                )
        return data

    def create(self, validated_data):
        '''Создания рецепта.'''
        with transaction.atomic():
            ingredients = validated_data.pop('ingredient_in_recipe')
            tags = validated_data.pop('tags')
            author = self.context.get('request').user
            recipe = Recipe.objects.create(
                author=author,
                **validated_data
            )
            create_relationship_tag_recipe(tags, recipe)
            create_relationship_ingredient_recipe(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        '''Обновления рецепта.'''
        with transaction.atomic():
            current_obj_recipe = get_object_or_404(Recipe, id=instance.pk)
            if validated_data.get('ingredient_in_recipe'):
                model = RecipeIngredientRelationship
                records_ingredient_recipe = model.objects.filter(
                    recipe=current_obj_recipe
                )
                for record in records_ingredient_recipe:
                    record.delete()
                ingredients = validated_data.pop('ingredient_in_recipe')
                create_relationship_ingredient_recipe(
                    ingredients,
                    current_obj_recipe
                )
            if validated_data.get('tags'):
                records_tag_recipe = RecipeTagRelationship.objects.filter(
                    recipe=current_obj_recipe
                )
                for record in records_tag_recipe:
                    record.delete()
                tags = validated_data.pop('tags')
                create_relationship_tag_recipe(tags, current_obj_recipe)
        return super().update(instance, validated_data)
