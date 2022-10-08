from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerialiser(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerialiser(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientCreate(RecipeIngredientSerialiser):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, amount):
        if amount < 1:
            raise serializers.ValidationError('Значение должно быть больше 0')
        return amount


class RecipeWriteSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, required=True, use_url=True)
    ingredients = RecipeIngredientCreate(many=True)

    class Meta:
        model = Recipe
        fields = [
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
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def validate(self, serialized_data):
        tags_data = serialized_data.pop('tags')
        ingredients_data = serialized_data.pop('ingredients')
        unique_ingredients = set()
        for ingredient in ingredients_data:
            if ingredient.get('amount') <= 0:
                raise exceptions.ValidationError(
                    'Количество ингредиентов должно быть больше нуля'
                )
            if ingredient['id'] in unique_ingredients:
                raise exceptions.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
            unique_ingredients.add(ingredient['id'])
        new_recipe = Recipe.objects.create(**serialized_data)

        tags = []

        for tag in tags_data:
            tag_object = get_object_or_404(Tag, id=tag.id)
            tags.append(tag_object)
        new_recipe.tags.add(*tags)

        for ingredient in ingredients_data:
            ingredient_object = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            new_recipe.ingredients.add(
                ingredient_object,
                through_defaults={'amount': ingredient.get('amount')}
            )
        new_recipe.save()
        return new_recipe

    def create(self, validated_data, serialized_data):
        request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags_data)
        author = serialized_data.get('author')
        name = serialized_data.get('name')
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        if Recipe.objects.filter(author=author, name=name).exists():
            raise exceptions.ValidationError(
                ('Вы уже публиковали рецепт с таким названием')
            )
        return RecipeIngredient.objects.bulk_create(objs)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        update = {}
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount']
            )
            for ingredient in ingredients_data
        ]
        for obj, amount in update.items():
            RecipeIngredient.objects.create(
                ingredient=obj, amount=amount, recipe=instance
            )
        instance.tags.set(tags_data)
        msg = RecipeIngredient.objects.bulk_create(objs)
        return super().update(instance, validated_data, msg)


class RecipeReadSerializer(RecipeWriteSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        ]


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if Favorite.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                {'errors': 'Нельзя повторно добавить в избранное'}
            )
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return validated_data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def validate(self, data):
        user = data['user']['id']
        recipe = data['recipe']['id']
        if ShoppingCart.objects.filter(user=user, recipe__id=recipe).exists():
            raise serializers.ValidationError(
                {"errors": "Вы уже добавили рецепт в корзину"}
            )
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return validated_data
