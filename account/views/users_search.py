from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from account.models import User
from rest_framework import serializers
from account.permissions import DynamicPermission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_picture', 'first_name', 'last_name', 'email', 'date_of_birth', 'mobile', 'bmu', 'referral_code']

class UserSearchView(generics.ListAPIView):
    """
    API to search users by bmu, mobile, email, or name.
    Only staff users (is_staff=True) can access this.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """Ensure only staff users can search"""
        user = self.request.user
        if not user.is_staff:
            return User.objects.none()  

        search_fields = ['bmu', 'mobile', 'email', 'name']
        query_params = self.request.query_params  

        # Ensure only one search key is provided
        if len(query_params) != 1:
            return User.objects.none()  
        key, value = list(query_params.items())[0]  

        # Validate key
        if key not in search_fields:
            return User.objects.none()

        # Perform filtering based on the key
        if key == "name":
            return User.objects.filter(Q(first_name__icontains=value) | Q(last_name__icontains=value))
        else:
            return User.objects.filter(**{f"{key}__icontains": value})

    def get(self, request, *args, **kwargs):
        """ Handle search requests, allow only staff users """
        user = request.user
        if not user.is_staff:
            return Response(
                {'message': 'You do not have permission to perform this action.'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        users = self.get_queryset()

        if not users.exists():
            return Response(
                {'message': 'No matching users found.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(users, many=True)
        return Response(
            {'message': 'Users retrieved successfully', 'data': serializer.data}, 
            status=status.HTTP_200_OK
        )
