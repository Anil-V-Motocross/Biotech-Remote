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
def banner(request):
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
    
    return Response(data={'message': 'Something went wrong.!'}, status=status.HTTP_400_BAD_REQUEST)