from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .pagination import UserPagination
from .serializers import (NewUserSerializer, SetPasswordSerializer,
                          SubscriptionsSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            return (permissions.AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return NewUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = get_object_or_404(User, email=request.user.email)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = get_object_or_404(User, email=request.user.email)
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            if check_password(request.data['current_password'], user.password):
                new_password = make_password(request.data['new_password'])
                user.password = new_password
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'current_password': 'Вы ввели неверный пароль'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            data=pages,
            many=True,
            context={
                'request': request
            },
        )
        serializer.is_valid()
        return self.get_paginated_response(data=serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        interes_user = get_object_or_404(User, id=pk)
        if request.method == 'POST':
            if request.user == interes_user:
                return Response(
                    {'errors': 'Невозможно подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif Follow.objects.filter(
                    following=interes_user,
                    user=request.user).exists():
                return Response(
                    {'errors': (
                        'Вы уже подписаны на пользователя '
                        + f'{interes_user.username}.'
                    )},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(following=interes_user, user=request.user)
            serializer = SubscriptionsSerializer(
                interes_user,
                context={
                    'request': request
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscribe = Follow.objects.filter(
            following=interes_user,
            user=request.user
        )
        if subscribe:
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': (
                'Вы не были подписаны на пользователя '
                + f'{interes_user.username}.'
            )},
            status=status.HTTP_400_BAD_REQUEST
        )
