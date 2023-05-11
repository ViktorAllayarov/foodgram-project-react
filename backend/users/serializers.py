# from api.serializers import RecipeAddToSerializer
from djoser.serializers import UserCreateSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from users.models import Subscriptions, User
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, CharField, ListSerializer, ReadOnlyField
from recipes.models import (AmountIngredient, Cart, Favorites, Ingredient,
                            Recipe, Tag)
from users.mixins import IsSubscribedMixin
from rest_framework.validators import UniqueValidator
from django.shortcuts import get_object_or_404


class RecipeAddToSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'password'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return Subscriptions.objects.filter(user=user, following=obj).exists()

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class SubscribeSerializer(ModelSerializer, IsSubscribedMixin):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        ]

    def get_recipes_count(self, data):
        return Recipe.objects.filter(author=data).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeAddToSerializer(recipes, many=True, read_only=True)
        
        return serializer.data
