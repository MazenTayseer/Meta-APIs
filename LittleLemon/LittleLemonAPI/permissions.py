from rest_framework.permissions import BasePermission

class IsAdminOrManagerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name="Managers").exists())