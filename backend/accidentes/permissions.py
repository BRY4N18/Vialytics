from rest_framework.permissions import BasePermission


class EsAnalista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
