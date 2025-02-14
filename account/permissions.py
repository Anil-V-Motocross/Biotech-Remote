from rest_framework.permissions import BasePermission

class DynamicPermission(BasePermission):
    def has_permission(self, request, view):
        # Retrieve required permissions (single or multiple)
        required_permissions = getattr(view, 'required_permissions', [])

        # If no permissions are defined, grant access
        if not required_permissions:
            return True

        # Ensure the user has ALL required permissions
        return all(request.user.has_perm(perm) for perm in required_permissions)
