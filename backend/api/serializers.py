from django.contrib.auth import get_user_model
from django.db.models import F
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CurrentUserDefault, SlugRelatedField

from api.mixins import IsSubscribedMixin
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from users.models import Subscriptions

User = get_user_model()


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous or (user == obj):
            return False
        return Subscriptions.objects.filter(user=user, following=obj).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


class SubscribeSerializer(ModelSerializer):
    following = SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
    )
    user = SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all(),
        default=CurrentUserDefault()
    )

    class Meta:
        model = Subscriptions
        fields = '__all__'

    def validate(self, data):
        author = data.get("following")
        user = data.get("user")
        if Subscriptions.objects.filter(following=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
            
        return data


class SubscriptionsSerializer(ModelSerializer, IsSubscribedMixin):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.GET.get("recipes_limit")
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeAddToSerializer(recipes, many=True, read_only=True)

        return serializer.data


class TagSerializer(ModelSerializer):
    """Сериализатор для вывода тэгов."""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientSerializer(ModelSerializer):
    """Сериализатор для вывода ингредиентов."""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeReadSerializer(ModelSerializer):
    """Сериализатор для чтения рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = (
            "is_favorite",
            "is_shopping_cart",
        )

    def get_ingredients(self, recipe):
        """Получает список ингридиентов для рецепта."""

        return recipe.ingredients.values(
            "id",
            "name",
            "measurement_unit",
            amount=F("amountingredient__amount"),
        )

    def get_is_favorited(self, recipe):
        """Находится ли рецепт в избранных."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False

        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """Находится ли рецепт в списке  покупок."""

        user = self.context.get("request").user
        if user.is_anonymous:
            return False

        return user.cart.filter(recipe=recipe).exists()


class IngredientInRecipeWriteSerializer(ModelSerializer):
    id = IntegerField(write_only=True)

    class Meta:
        model = AmountIngredient
        fields = ("id", "amount")


class RecipeWriteSerializer(ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {"ingredients": "Нужен хотя бы один ингредиент!"}
            )
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item["id"])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {"ingredients": "Ингридиенты не могут повторяться!"}
                )
            if int(item["amount"]) <= 0:
                raise ValidationError(
                    {"amount": "Количество ингредиента должно быть больше 0!"}
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({"tags": "Нужно выбрать хотя бы один тег!"})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {"tags": "Теги должны быть уникальными!"}
                )
            tags_list.append(tag)
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        AmountIngredient.objects.bulk_create(
            [
                AmountIngredient(
                    ingredient=Ingredient.objects.get(id=ingredient["id"]),
                    recipe=recipe,
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeAddToSerializer(ModelSerializer):
    """Сериализатор для модели Recipe."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("__all__",)
