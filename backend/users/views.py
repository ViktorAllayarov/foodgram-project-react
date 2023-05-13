from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.paginators import PageLimitPagination
from users.models import Subscriptions, User
from users.serializers import SubscribeSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, **kwargs):
        user = request.user
        author_id = self.kwargs.get("id")
        author = get_object_or_404(User, id=author_id)
        if request.method == "POST":
            if user == author:
                raise ValidationError("Вы не можете подписаться на самого себя!")
            if Subscriptions.objects.filter(following=author, user=user).exists():
                raise ValidationError("Вы уже подписаны!")
            serializer = SubscribeSerializer(author, context={"request": request})
            Subscriptions.objects.create(user=user, following=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            subscription = get_object_or_404(Subscriptions, user=user, following=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pages, many=True, context={"request": request})

        return self.get_paginated_response(serializer.data)
