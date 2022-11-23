from rest_framework.permissions import BasePermission
from django.contrib.auth.models import User


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user.pk == obj.username_id and request.user.is_authenticated)
