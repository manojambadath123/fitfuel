
from rest_framework.permissions import BasePermission

class Isowner(BasePermission):

    def has_object_permission(self, request, view, obj):
        
        return request.user == obj.user

class HasProfile(BasePermission):

    message = "your profile setup has not completed"

    def has_permission(self, request, view):
        
        try:
            user_profile = request.user.profile

            if user_profile:

                return True
            else:
                return False

        except Exception as e:

            return False 