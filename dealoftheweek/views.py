from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DealOfTheWeek
from .serializers import AdminDealOfTheWeekSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from account.permissions import DynamicPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

# class ActiveDealOfTheWeekView(APIView):
#     def get(self, request):
#         deal = DealOfTheWeek.objects.filter(is_active=True).order_by('-start_date').first()  
#         if deal:
#             product_id = deal.main_products.id 
#             return Response(data={"main_product_id": product_id})
#         return Response({"main_product_id": None})

class ActiveDealOfTheWeekView(APIView):
    def get(self, request):
        today = timezone.now()  # Get the current server time

        active_deal = DealOfTheWeek.objects.filter(
            is_active=True,        # Ensure deal is active
            start_date__lte=today, # Start date must be before or equal to today
            end_date__gte=today    # End date must be after or equal to today
        ).order_by('end_date').first()  # Select the deal with the nearest end date

        if active_deal:
            product_id = active_deal.main_products.id
            return Response(data={"main_product_id": product_id})

        return Response({"main_product_id": None}) 


# ******** Admin side ******** 
class DealOfTheWeekListCreateView(generics.ListCreateAPIView):
    """
    Handles listing all deals and creating a new deal (Only staff users with the correct permissions).
    """
    queryset = DealOfTheWeek.objects.all()
    serializer_class = AdminDealOfTheWeekSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff or not request.user.has_perm('dealoftheweek.view_dealoftheweek'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        deals = self.get_queryset()
        

        serializer = self.get_serializer(deals, many=True)
        return Response({'message': 'Deals retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not request.user.is_staff or not request.user.has_perm('dealoftheweek.add_dealoftheweek'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        print("deals - data :", request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Deal created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DealOfTheWeekDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting a deal (Only staff users with correct permissions).
    """
    queryset = DealOfTheWeek.objects.all()
    serializer_class = AdminDealOfTheWeekSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    authentication_classes = [JWTAuthentication]

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff or not request.user.has_perm('dealoftheweek.view_dealoftheweek'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            deal = self.get_object()
            serializer = self.get_serializer(deal)
            return Response({'message': 'Deal retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        except DealOfTheWeek.DoesNotExist:
            return Response({'message': 'Deal not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        if not request.user.is_staff or not request.user.has_perm('dealoftheweek.change_dealoftheweek'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            deal = self.get_object()
            serializer = self.get_serializer(deal, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Deal updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except DealOfTheWeek.DoesNotExist:
            return Response({'message': 'Deal not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff or not request.user.has_perm('dealoftheweek.delete_dealoftheweek'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            deal = self.get_object()
            deal.delete()
            return Response({'message': 'Deal deleted successfully'}, status=status.HTTP_200_OK)
        except DealOfTheWeek.DoesNotExist:
            return Response({'message': 'Deal not found'}, status=status.HTTP_404_NOT_FOUND)


