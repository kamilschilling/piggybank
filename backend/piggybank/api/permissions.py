from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyForChild(BasePermission):

    def has_permission(self, request, view):
        try:
            request.user.parent.isParent
        except:
            return request.method in SAFE_METHODS
        return True


class ReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class WithoutPost(BasePermission):

    def has_permission(self, request, view):
        return request.method != "POST"
