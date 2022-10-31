from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from users.models import Follow
from .permissions import IsAuthorOnly
from .serializers import FollowSerializer, ShowFollowSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthorOnly,),
    )
    def subscriptions(self, request):
        user = User.objects.filter(following__user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        page = paginator.paginate_queryset(user, request)
        serializer = ShowFollowSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=['GET', 'DELETE'],
        url_name='subscribe',
        url_path='subscribe',
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(data={'user': user.id, 'author': id})
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            serializer = ShowFollowSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        obj = get_object_or_404(Follow, user=user, author__id=id)
        obj.delete()
        return Response('Подписка удалена', status=status.HTTP_204_NO_CONTENT)
