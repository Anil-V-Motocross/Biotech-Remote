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
def login_staff(request):
    if request.method == 'POST':
        # Get the email and password from the request data
        mobile = request.data.get('mobile')
        password = request.data.get('password')
        
        if not mobile or not password:
            return Response({'message': 'Mobile and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if the user exists in the database
        user = User.objects.filter(mobile=mobile).first()
        
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
