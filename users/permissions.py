from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
        Разрешает полный доступ владельцу профиля, только чтение всем остальным пользователям.
        """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user