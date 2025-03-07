from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from coupon.models import Coupon
from coupon.serializers import CouponSerializer
from django.shortcuts import get_object_or_404
from django.db.models import F  

class AvailableCouponsView(APIView):
    """API to fetch all active and valid coupons with custom error handling."""
    
    def get(self, request):
        print(Coupon._meta.app_label)
        try:
            now = timezone.now()
            
            # Fetch only active coupons that are within the valid date range
            coupons = Coupon.objects.filter(
                active=True, 
                start_date__lte=now, 
                end_date__gte=now
            )

            # Exclude coupons that have reached their usage limit
            coupons = coupons.exclude(usage_limit__isnull=False, used_count__gte=F('usage_limit'))

            if not coupons.exists():
                return Response(
                    data={"message": "No available coupons at the moment."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CouponSerializer(coupons, many=True)
            return Response(
                data={"message": "Available coupons retrieved successfully.", "coupons": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                data={"error": "Something went wrong while retrieving coupons.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SingleCouponView(APIView):
    """API to fetch a single valid coupon by its ID with error handling."""

    def get(self, request, coupon_id):
        try:
            # Fetch the coupon and ensure it is active, within date range, and usage limit not exceeded
            coupon = get_object_or_404(
                Coupon, 
                id=coupon_id, 
                active=True, 
                start_date__lte=timezone.now(), 
                end_date__gte=timezone.now()
            )

            # Check if usage limit is exceeded
            if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
                return Response(
                    data={"message": "This coupon has reached its usage limit and is no longer available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = CouponSerializer(coupon)
            return Response(
                data={"message": "Coupon retrieved successfully.", "coupon": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                data={"error": "Something went wrong while retrieving the coupon.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
