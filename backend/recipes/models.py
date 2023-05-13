from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Класс модель тегов для рецептов."""

    name = models.CharField(
        verbose_name="Название", unique=True, max_length=200
    )
    color = models.CharField(
        verbose_name="Цветовой HEX-код",
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message="Введенное значение не является цветом в формате HEX!",
            )
        ],
    )
    slug = models.SlugField(
        verbose_name="Уникальный слаг",
        unique=True,
        max_length=200,
        validators=[
            RegexValidator(
                regex="^[-a-zA-Z0-9_]+$",
                message="Введенное значение не соответствует формату!",
            )
        ],
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс модель ингредиентов."""

    name = models.CharField(
        verbose_name="Ингредиент",
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ("-id",)


class Recipe(models.Model):
    """Класс модель рецептов."""

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Ингредиенты блюда",
        through="AmountIngredient",
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Теги"
    )
    image = models.ImageField(
        verbose_name="Изображение", upload_to="recipe_images/"
    )
    name = models.CharField(
        verbose_name="Название",
        max_length=200,
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[MinValueValidator(1, message="Минимальное значение 1!")],
    )
    author = models.ForeignKey(
        User,
        related_name="recipes",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Автор рецепта",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ("-id",)

    def __str__(self):
        return self.name


class AmountIngredient(models.Model):
    """Класс модель описывает количество ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_list",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[MinValueValidator(1, message="Минимальное количество 1!")],
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Количество ингредиентов"
        ordering = ("recipe",)


class Cart(models.Model):
    """Класс модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзина покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_cart"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Корзину покупок'


class Favorites(models.Model):
    """Класс модель для добавления рецепта в избранное."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favourite"
            )
        ]

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'
