from rest_framework.permissions import BasePermission


class IsSuperUserOrReadOnly(BasePermission):
    """
    Allows access only to superusers. Others can only read (GET).
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_superuser:
            return True
        return request.method in ['GET', 'HEAD', 'OPTIONS']
