from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from account.models import User


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        # Get the email and password from the request data
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        if not phone_number or not password:
            return Response({'message': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user exists in the database
        user = User.objects.filter(phone_number=phone_number).first()
        
        if user and user.check_password(password):
            # add access token and refresh token to response
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data={'token': token, 'message': 'Login successful'}, status=status.HTTP_200_OK)
        else:
            # User authentication failed
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
