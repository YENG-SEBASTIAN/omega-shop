from rest_framework.permissions import BasePermission, IsAuthenticated

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit products.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to the admin
        return request.user and request.user.is_staff
