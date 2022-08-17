from rest_framework import permissions


class AdminAllOnlyAuthorPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user.is_superuser
            or obj.author == request.user
            or request.user.groups.filter(name='recipes_admins').exists()
        )
