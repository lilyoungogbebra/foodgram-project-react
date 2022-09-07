from rest_framework import permissions


class UserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'create', 'retrieve'] and (
            request.user.is_authenticated or request.user.is_anonymous
             ):
            return True
        elif request.method in ['DELETE', 'POST', 'GET'] and (
            request.user.is_authenticated
             ):
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in ['DELETE', 'POST', 'GET'] and (
            request.user.is_superuser
             ):
            return True
        elif request.method == 'DELETE' and (
            request.user.is_authenticated
             ):
            subscriptions = obj.following.filter(user=request.user).exists()
            return subscriptions
        elif request.method == 'POST' and request.user.is_authenticated:
            return True
        elif request.method == 'GET' and view.action == 'list' and (
            request.user.is_authenticated
             ):
            return obj == request.user
        elif request.method == 'GET' and view.action == 'retrieve' and (
            request.user.is_authenticated or request.user.is_anonymous
             ):
            return True
