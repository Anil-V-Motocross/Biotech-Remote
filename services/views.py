# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Service_enquiry
from .models import Servicelist
from .serializers import ServiceEnquirySerializer
from .serializers import ServiceListSerializer
from account.permissions import DynamicPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

@api_view(['POST'])
def create_service_enquiry(request):
    if request.method == 'POST':
        serializer = ServiceEnquirySerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the new Service Enquiry record
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def get_service_enquiries(request):
    if request.method == 'GET':
        required_permissions = [
            'services.view_service_enquiry',
            'services.add_service_enquiry',
        ]
        
        # print("User permissions:", request.user.get_all_permissions())
        # print("Required permissions:", required_permissions)
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        service_enquiries = Service_enquiry.objects.all()
        serializer = ServiceEnquirySerializer(service_enquiries, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)



   
@api_view(['POST'])
def create_servicelist(request):
    if request.method == 'POST':
        serializer = ServiceListSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the new Service List record
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
