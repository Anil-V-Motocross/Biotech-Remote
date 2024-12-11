from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from promotion.models import Banner
from rest_framework import serializers


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

@api_view(['GET'])
def banner(request, pk=None):
    if request.method == 'GET':
        # required_permissions = []
        
        # if not any(request.user.has_perm(perm) for perm in required_permissions):
        #     return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        banner = Banner.objects.all()
        serializer = BannerSerializer(banner, many=True)
        data = {
            'banners': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'promotion.view_banner'
        ]
    
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Banner.objects.filter(id=pk).exists():
            banner = Banner.objects.get(id=pk)
            serializer = BannerSerializer(banner)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Banner does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':
        required_permissions = [
            'promotion.add_banner'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'promotion.change_banner'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Banner.objects.filter(id=pk).exists():
            banner = Banner.objects.get(id=pk)
            serializer = BannerSerializer(banner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Banner does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        required_permissions = [
            'promotion.delete_banner'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Banner.objects.filter(id=pk).exists():
            banner = Banner.objects.get(id=pk)
            banner.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Banner does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(data={'message': 'Something went wrong.!'}, status=status.HTTP_400_BAD_REQUEST)