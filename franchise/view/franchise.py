from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from franchise.models import FranchiseEnquiry
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework.decorators import authentication_classes, permission_classes


class FranchiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FranchiseEnquiry
        fields = '__all__'

@api_view(['GET','PATCH','DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def franchise(request,pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'franchise.view_franchise'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        franchises = Franchise.objects.all()
        serializer = FranchiseSerializer(franchises, many=True)
        data = {
            'franchises': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)



    if request.method == 'GET' and pk:
        required_permissions = [
            'franchise.view_franchise'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        if Franchise.objects.filter(id=pk).exists():
            franchise_instance = Franchise.objects.get(id=pk)
            serializer = FranchiseSerializer(franchise_instance)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'franchise does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH'  :
        required_permissions = [
            'franchise.change_franchise'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        franchise_id = request.data.get('franchise_id')
        if not franchise_id:
            return Response(data={'message': 'franchise ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Franchise.objects.filter(id=franchise_id).exists():
            franchise_instance = Franchise.objects.get(id=franchise_id)
            franchise_instance.save()

            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)

        return Response(data={'message': 'franchise not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method=='DELETE' and pk:
        required_permissions = [
            'franchise.delete_franchise'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'},
                            status=status.HTTP_403_FORBIDDEN)

        if Franchise.objects.filter(id=pk).exists():
            franchise = Franchise.objects.get(id=pk)
            franchise.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'franchises not not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

    