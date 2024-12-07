from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from account.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    # also check password Invalid password format or unknown hashing algorithm.
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

@api_view(['POST'])
def register_staff(request):
    if request.method == 'POST':
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        if serializer.errors:
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)