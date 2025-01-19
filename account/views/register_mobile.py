from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from account.models import InitialInfo
from rest_framework_simplejwt.tokens import RefreshToken

import requests

from account.models import User

# generate 6 digit otp
def generate_otp():
    import random
    return str(random.randint(1111, 9999))

def gererate_password():
    # make password of 20 characters including special characters, numbers, and uppercase and lowercase letters
    import random
    import string
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(20))


def send_otp(mobile, otp):
    phone = "91" + str(mobile)
    # print(user["mobile"])
    # print(user["otp"])
    try:
        # =======================================================================
        url = "https://control.msg91.com/api/v5/flow/"
        # payload = {"template_id": "60ffda6d9c235f799241960f",
        #            "recipients": [{"mobiles": phone, "name": name, "otp": otp}]}  674a89f9d6fc05032f5bf902
        payload = {"template_id": "60ffda6d9c235f799241960f",
                   "recipients": [{
                       "mobiles": phone,
                       "name": "ABC",
                       "otp": otp
                   }]
                   }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            # "authkey": "433172AwxmUdTOWK6746d6c2P1"
            "authkey": "112997AWvDqQDssV665ba34edP1"
        }

        response = requests.post(url, json=payload, headers=headers)
        for i in response:
            print(i)
        # =======================================================================
        return True
    except Exception as e:
        # print(e)
        return False

class RegisteMOBileRegisterSerializer(serializers.ModelSerializer):

    mobile = serializers.CharField(max_length=255)
    class Meta:
        model = InitialInfo
        fields = ['mobile']

    def validate_mobile(self, value):
        
        # mobile 10 digits and all digit
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Mobile number must be 10 digits.")
        return value
    

@api_view(['POST'])
def register_mobile(request):
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)

        if not mobile:
            return Response(data={'message': 'Mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check mobile is exists in User model with mobile
        if User.objects.filter(mobile=mobile).exists():
            # Generate OTP
            otp = generate_otp()
            # update otp in User model
            User.objects.filter(mobile=mobile).update(otp=otp)
            # send otp
            send_otp(mobile=mobile, otp=otp)
            return Response(data={'message': 'Registered User.', 'mobile': mobile}, status=status.HTTP_200_OK)
        
        # mobile is exists send otp with status 200
        if InitialInfo.objects.filter(mobile=mobile).exists():
            # Generate OTP
            otp = generate_otp()
            InitialInfo.objects.filter(mobile=mobile).update(otp=otp)
            # send otp
            send_otp(mobile=mobile, otp=otp)
            return Response(data={'message': 'Only registered with mobile number.', 'mobile': mobile}, status=status.HTTP_201_CREATED)

        serializer = RegisteMOBileRegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Generate OTP
            otp = generate_otp()
            serializer.validated_data['otp'] = otp
            # send otp
            send_otp(mobile=mobile, otp=otp)
            # Save the new Service Enquiry record
            serializer.save()
            return Response(data={'message': 'Mobile number registered successfully.', 'mobile': mobile}, status=status.HTTP_201_CREATED)
        # also check password Invalid password format or unknown hashing algorithm.

        if serializer.errors:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# validate otp
@api_view(['POST'])
def validate_otp(request):
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)
        otp = request.data.get('otp', None)
        if not mobile or not otp:
            return Response(data={'message': 'Mobile number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check mobile is exists in User model with mobile
        if User.objects.filter(mobile=mobile).exists():
            # check otp request and database
            if not User.objects.filter(mobile=mobile, otp=otp).exists():
                return Response(data={'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
                # pass
            
            # Attach jwt token
            user = User.objects.filter(mobile=mobile).first()
            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            # attach user details
            data = {
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'mobile': user.mobile,
                },
                'token': token
            }
            # update otp in User model to None
            user.otp = None
            user.save()

            return Response(data={'data': data, 'message': 'OTP is valid. and registered User.'}, status=status.HTTP_200_OK)

        # check otp request and database
        if not InitialInfo.objects.filter(mobile=mobile).exists():
            return Response(data={'message': 'Mobile number does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        # check request otp and database otp
        if not InitialInfo.objects.filter(mobile=mobile, otp=otp).exists():
            return Response(data={'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if InitialInfo.objects.filter(mobile=mobile, otp=otp).exists():
            return Response(data={'message': 'OTP is valid. and only registered with mobile number.', 'mobile': mobile}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    

class InitialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialInfo
        fields = ['name', 'email', 'referal_code']
    

# Take other fields of InitialInfo
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)
        name = request.data.get('name', None)
        referal_code = request.data.get('referal_code', None)

        if not mobile or not name:
            return Response(data={'message': 'Mobile number, name, code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # check mobile is exists in User model with mobile
        if User.objects.filter(mobile=mobile).exists():
            return Response(data={'message': 'Mobile number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # make email field by concatenating mobile number and save in User model and delete in InitialInfo model
        data = {
                "password": gererate_password(),
                "first_name": name,
                "mobile": mobile,
                "email": f"{mobile}@example.com",
                "referal_code": referal_code,
                "is_active": True
            }
        user = User.objects.create_user(**data)
        user.save()
        
         # Add the user to the 'Customer' group
        customer_group, created = Group.objects.get_or_create(name='Customer')
        user.groups.add(customer_group)
        
        InitialInfo.objects.filter(mobile=mobile).delete()
        # attech jwt token
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        # attach user de
        data = {
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'mobile': user.mobile,
            },
            'token': token
        }
        return Response(data={'data': data, 'message': 'User registered successfully.'}, status=status.HTTP_200_OK)