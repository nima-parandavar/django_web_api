from rest_framework.request import HttpRequest
from rest_framework.permissions import BasePermission, SAFE_METHODS
from image.models import *


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request: HttpRequest, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff or request.user.is_superuser)


class IsSelfOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user == obj


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, Image):
            return bool(request.user and request.user.is_authenticated and
                    obj.photographer.id == request.user.id)

        if isinstance(obj, Collection):
            return bool(request.user and request.user.is_authenticated and
                        obj.user.id == request.user.id)
