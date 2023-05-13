import io
from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import PageLimitPagination
from api.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeAddToSerializer,
                             RecipeReadSerializer, RecipeWriteSerializer,
                             TagSerializer)
from recipes.models import (AmountIngredient, Cart, Favorites, Ingredient,
                            Recipe, Tag)


class TagViewSet(ReadOnlyModelViewSet):
    """Класс для работы с тегами."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    """Класс для работы с ингредиентами."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """Класс для работы с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer

        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        if request.method == "POST":
            return self.add_to(Favorites, request.user, pk)
        return self.delete_from(Favorites, request.user, pk)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        if request.method == "POST":
            return self.add_to(Cart, request.user, pk)
        return self.delete_from(Cart, request.user, pk)

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {"errors": "Рецепт уже добавлен!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeAddToSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {"errors": "Рецепт уже удален!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = (
            AmountIngredient.objects.filter(recipe__cart__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
        )
        final_ingredients_list = {}
        for item in ingredients:
            name = item["ingredient__name"]
            if name not in final_ingredients_list:
                final_ingredients_list[name] = {
                    "measurement_unit": item["ingredient__measurement_unit"],
                    "amount": item["amount"],
                }
            else:
                final_ingredients_list[name]["amount"] += item["amount"]
        print(final_ingredients_list)
        pdfmetrics.registerFont(
            TTFont("Roboto-Regular", "Roboto-Regular.ttf", "UTF-8")
        )
        filename = f"{user.username}_shopping_list"

        buffer = io.BytesIO()
        width, height = A4
        text_page = canvas.Canvas(buffer, pagesize=A4)

        textobject = text_page.beginText()
        textobject.setFont("Roboto-Regular", size=10)
        textobject.setTextOrigin(30, height - 40)
        textobject.textLine(text=f"Дата: { datetime.today():%Y-%m-%d }")
        textobject.textLine(text="")
        textobject.setFont("Roboto-Regular", size=14)
        textobject.textLine(text="Список ингредиентов:")
        textobject.setFont("Roboto-Regular", size=12)
        textobject.textLine(text="")
        [
            textobject.textLine(
                text=f"- {ingredient} "
                f'({amount["measurement_unit"]})'
                f' - {amount["amount"]}'
            )
            for ingredient, amount in final_ingredients_list.items()
        ]

        text_page.drawText(textobject)
        text_page.showPage()
        text_page.save()
        buffer.seek(0)

        # для .txt "text/plain",
        # для .pdf "application/pdf"
        response = HttpResponse(buffer, content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = f"attachment; filename={filename}.pdf"

        return response
