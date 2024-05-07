from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsUserRegistration(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return False


class IsUserUpdate(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'PATCH':
            return bool(request.user and request.user == obj)
        return False


class IsSuperuser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


# class IsOwnerOrSuperuser(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method == 'GET':
#             return True
#         return bool(request.user and
#                     (request.user == obj.user or request.user.is_superuser))

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user == obj.user)
