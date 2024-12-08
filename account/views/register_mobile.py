from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from account.models import InitialInfo

import requests

# generate 6 digit otp
def generate_otp():
    import random
    return str(random.randint(100000, 999999))


def send_otp(mobile, otp):
    phone = "91" + str(mobile)
    # print(user["phone_number"])
    # print(user["otp"])
    try:
        # =======================================================================
        url = "https://control.msg91.com/api/v5/flow/"
        # payload = {"template_id": "60ffda6d9c235f799241960f",
        #            "recipients": [{"mobiles": phone, "name": name, "otp": otp}]}
        payload = {"template_id": "65bb4b91d6fc0562db225202",
                   "recipients": [{
                       "mobiles": phone,
                       "name": "Rahul",
                       "otp": otp
                   }]
                   }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": "112997AX953OZo28W63788920P1"
        }

        response = requests.post(url, json=payload, headers=headers)
        # for i in response:
        #     print(i)
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
    
    @property
    def errors(self):
        errors = super().errors
        # Flatten errors for group_name if it exists
        if "mobile" in errors and isinstance(errors["mobile"], list):
            errors["mobile"] = errors["mobile"][0]
        return errors

@api_view(['POST'])
def register_mobile(request):
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)

        if not mobile:
            return Response({'message': 'Mobile number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # mobile is exists send otp with status 200
        if InitialInfo.objects.filter(mobile=mobile).exists():
            # Generate OTP
            otp = generate_otp()
            InitialInfo.objects.filter(mobile=mobile).update(otp=otp)
            # send otp
            send_otp(mobile=mobile, otp=otp)
            return Response({'message': 'Mobile number already exists.'}, status=status.HTTP_200_OK)

        serializer = RegisteMOBileRegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Generate OTP
            otp = generate_otp()
            serializer.validated_data['otp'] = otp
            # send otp
            send_otp(mobile=mobile, otp=otp)
            # Save the new Service Enquiry record
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            return Response({'message': 'Mobile number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)
        # check otp request and database
        if not InitialInfo.objects.filter(mobile=mobile).exists():
            return Response({'message': 'Mobile number does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        # check request otp and database otp
        if not InitialInfo.objects.filter(mobile=mobile, otp=otp).exists():
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        if InitialInfo.objects.filter(mobile=mobile, otp=otp).exists():
            return Response({'message': 'OTP is valid.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
    

class InitialInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialInfo
        fields = ['name', 'email', 'referell_code']
    

# Take other fields of InitialInfo
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        mobile = request.data.get('mobile', None)
        name = request.data.get('name', None)
        email = request.data.get('email', None)

        if not mobile or not name or not email:
            return Response({'message': 'Mobile number, name, email and referell code are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # email should be unique
        if InitialInfo.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        

        serializer = InitialInfoSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the new Service Enquiry record
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)