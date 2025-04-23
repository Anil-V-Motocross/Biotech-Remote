from rest_framework.permissions import BasePermission

class DynamicPermission(BasePermission):
    def has_permission(self, request, view):
        # Only allow staff users
        # if not request.user.is_staff:
        #     return False
        # Retrieve required permissions (single or multiple)
        required_permissions = getattr(view, 'required_permissions', [])

        # If no permissions are defined, grant access
        if not required_permissions:
            return True

        # Ensure the user has ALL required permissions
        return all(request.user.has_perm(perm) for perm in required_permissions)
    
class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff    
