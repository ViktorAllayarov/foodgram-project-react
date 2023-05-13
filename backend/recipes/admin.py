from django.contrib import admin
from django.contrib.admin import display, site

from recipes.models import (
    AmountIngredient,
    Cart,
    Favorites,
    Ingredient,
    Recipe,
    Tag,
)

site.site_header = "Админ панель Foodgram"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "author", "added_in_favorites")
    readonly_fields = ("added_in_favorites",)
    list_filter = (
        "author",
        "name",
        "tags",
    )

    @display(description="Количество в избранных")
    def added_in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )


@admin.register(Cart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(Favorites)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )


@admin.register(AmountIngredient)
class IngredientInRecipe(admin.ModelAdmin):
    list_display = (
        "recipe",
        "ingredient",
        "amount",
    )
