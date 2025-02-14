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

@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def get_service_enquiries(request,pk=None):
    if request.method == 'GET' and not  pk:
        required_permissions = [
            'services.view_service_enquiry',
            # 'services.add_service_enquiry',
        ]
                       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        service_enquiries = Service_enquiry.objects.all()
        serializer = ServiceEnquirySerializer(service_enquiries, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method=='GET' and pk:
        required_permissions = [
            'services.view_service_enquiry',

        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if Service_enquiry.objects.filter(id=pk).exists():
            service_enquiry = Service_enquiry.objects.get(id=pk)
            serializer=ServiceEnquirySerializer(service_enquiry)
            data={
                'service_enquiry':serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message':'service_enquuiry not found'},status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH' :

        required_permissions = [
           'services.change_service_enquiry'
        ]


        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        service_id = request.data.get('service_id')
        if not service_id:
            return Response(data={'message': 'ServiceEnquiry ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Service_enquiry.objects.filter(id=service_id).exists():
            service_enquiry= Service_enquiry.objects.get(id=service_id)
            serializer = ServiceEnquirySerializer(instance=service_enquiry, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Service-enquiry not found.'}, status=status.HTTP_404_NOT_FOUND)


    if request.method=='DELETE'and pk:
        required_permissions = [
            'services.delete_service_enquiry'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        if Service_enquiry.objects.filter(id=pk).exists():
            service_eq = Service_enquiry.objects.get(id=pk)
            service_eq.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'serviceenquiry not not found.'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def publicservicelist(request):

    if request.method == 'GET':

        service_list = Servicelist.objects.all()
        serializer = ServiceListSerializer(service_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response({'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated,DynamicPermission])
@authentication_classes([JWTAuthentication])
def servicelist(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'services.view_servicelist'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        service = Servicelist.objects.all()
        serializer = ServiceListSerializer(service, many=True)
        data = {
            'service': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    if request.method == 'GET' and not pk:
        required_permissions = [
            'services.view_servicelist'
        ]



        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Fetch all servicelist entries
        services = Servicelist.objects.all()
        serializer=ServiceListSerializer(services, many=True)
        data = {
            'services': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    if request.method == 'GET' and pk:
        required_permissions = ['services.view_servicelist']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
         return Response(data={'message': 'You do not have permission to perform this action.'},
                             status=status.HTTP_403_FORBIDDEN)


        # Fetch specific servicelist entry by id
        if Servicelist.objects.filter(id=pk).exists():
            service = Servicelist.objects.get(id=pk)
            serializer = ServiceListSerializer(service)
            data = {
                'service': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        required_permissions = [
            'services.add_servicelist'

        ]
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Create a new servicelist entry
        serializer = ServiceListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
     
        required_permissions = [
            'services.change_servicelist'
        ]
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        # Update an existing servicelist entry
        service_id = request.data.get('service_id')
        if not service_id:
            return Response(data={'message': 'id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Servicelist.objects.filter(id=service_id).exists():
            service = Servicelist.objects.get(id=service_id)
            serializer = ServiceListSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE' and pk:
        required_permissions = [
            'services.delete_servicelist'
        ]
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)


        if Servicelist.objects.filter(id=pk).exists():
            service = Servicelist.objects.get(id=pk)
            service.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Service not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Something went wrong!'}, status=status.HTTP_400_BAD_REQUEST)
