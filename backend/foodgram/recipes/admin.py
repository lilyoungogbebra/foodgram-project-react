from django.contrib import admin

from .models import (FavoritesRecipesUserList, Ingredient, Recipe,
                     RecipeIngredientRelationship, RecipeTagRelationship,
                     ShoppingUserList, Tag)


class RecipeInline(admin.TabularInline):
    model = RecipeTagRelationship


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'name',
        'calc_in_users_favorites',
    )
    list_filter = ('author', 'name', 'tags',)
    inlines = [RecipeInline, ]

    def calc_in_users_favorites(self, obj):
        return FavoritesRecipesUserList.objects.filter(recipe=obj).count()

    class Meta:
        model = Recipe


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit'
    )
    ordering = ('pk',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'slug',
        'color'
    )


class RecipeTagRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'tag',
        'recipe',
    )


class RecipeIngredientRelationshipAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
    )


class FavoritesRecipesUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


class ShoppingUserListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTagRelationship, RecipeTagRelationshipAdmin)
admin.site.register(
    RecipeIngredientRelationship,
    RecipeIngredientRelationshipAdmin
)
admin.site.register(FavoritesRecipesUserList, FavoritesRecipesUserListAdmin)
admin.site.register(ShoppingUserList, ShoppingUserListAdmin)
