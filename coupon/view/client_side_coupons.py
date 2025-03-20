from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from coupon.models import Coupon
from coupon.serializers import CouponSerializer
from django.shortcuts import get_object_or_404
from django.db.models import F  
from product.models import ProductCategory,Product
from order.models import Order, OrderItem
from rest_framework.permissions import IsAuthenticated

# class AvailableCouponsView(APIView):
#     """API to fetch all active and valid coupons with custom error handling."""
    
#     def get(self, request):
#         print(Coupon._meta.app_label)
#         try:
#             now = timezone.now()
            
#             # Fetch only active coupons that are within the valid date range
#             coupons = Coupon.objects.filter(
#                 active=True, 
#                 start_date__lte=now, 
#                 end_date__gte=now
#             )

#             # Exclude coupons that have reached their usage limit
#             coupons = coupons.exclude(usage_limit__isnull=False, used_count__gte=F('usage_limit'))

#             if not coupons.exists():
#                 return Response(
#                     data={"message": "No available coupons at the moment."},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             serializer = CouponSerializer(coupons, many=True)
#             return Response(
#                 data={"message": "Available coupons retrieved successfully.", "coupons": serializer.data},
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 data={"error": "Something went wrong while retrieving coupons.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )



# class SingleCouponView(APIView):
#     """API to fetch a single valid coupon by its ID with error handling."""

#     def get(self, request, coupon_id):
#         try:
#             # Fetch the coupon and ensure it is active, within date range, and usage limit not exceeded
#             coupon = get_object_or_404(
#                 Coupon, 
#                 id=coupon_id, 
#                 active=True, 
#                 start_date__lte=timezone.now(), 
#                 end_date__gte=timezone.now()
#             )

#             # Check if usage limit is exceeded
#             if coupon.usage_limit is not None and coupon.used_count >= coupon.usage_limit:
#                 return Response(
#                     data={"message": "This coupon has reached its usage limit and is no longer available."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             serializer = CouponSerializer(coupon)
#             return Response(
#                 data={"message": "Coupon retrieved successfully.", "coupon": serializer.data},
#                 status=status.HTTP_200_OK
#             )

#         except Exception as e:
#             return Response(
#                 data={"error": "Something went wrong while retrieving the coupon.", "details": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

class AvailableCouponsView(APIView):
    """API to fetch all active and valid coupons with custom error handling."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            now = timezone.now()
            user = request.user  # Assuming authentication is enabled

            # Get order_id from request params
            order_id = request.query_params.get("order_id")
            print(f"Received request for available coupons. User: {user}, Order ID: {order_id}")

            order, is_first_order, ordered_product_ids, ordered_categories = self.get_order_details(user, order_id)
            print(f"Order details fetched: {order}, Is First Order: {is_first_order}")
            print(f"Ordered Product IDs: {ordered_product_ids}, Ordered Categories: {ordered_categories}")

            # Fetch only active coupons that are within the valid date range
            coupons = Coupon.objects.filter(
                active=True,
                start_date__lte=now,
                end_date__gte=now
            ).exclude(usage_limit__isnull=False, used_count__gte=F('usage_limit'))

            print(f"Found {coupons.count()} active coupons before filtering.")

            if not coupons.exists():
                print("No available coupons found.")
                return Response(
                    {"message": "No available coupons at the moment."},
                    status=status.HTTP_404_NOT_FOUND
                )

            applicable_coupons = []
            for coupon in coupons:
                is_applicable = self.is_coupon_applicable(coupon, is_first_order, ordered_product_ids, ordered_categories)
                print(f"Coupon ID: {coupon.id}, Applicable: {is_applicable}")

                coupon_data = CouponSerializer(coupon).data
                coupon_data["is_applicable"] = is_applicable  # Add applicability flag
                applicable_coupons.append(coupon_data)

            print(f"Returning {len(applicable_coupons)} applicable coupons.")
            return Response(
                {"message": "Available coupons retrieved successfully.", "coupons": applicable_coupons},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error retrieving coupons: {e}")
            return Response(
                {"error": "Something went wrong while retrieving coupons.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_order_details(self, user, order_id):
        """Fetch order details including products and categories based on order_id or latest order."""
        print(f"Fetching order details for user: {user}, Order ID: {order_id}")
        
        if order_id:
            order = get_object_or_404(Order, id=order_id, customer_id=user.id)
            print(f"Order found: {order}")
        else:
            order = Order.objects.filter(customer_id=user.id).order_by('-date').first()
            print(f"Latest order found: {order}")

            if not order:
                print("No orders found. Assuming first order.")
                return None, True, [], []  # If no order exists, assume it's the first order

        is_first_order = not Order.objects.filter(customer_id=user.id).exclude(id=order.id).exists()
        ordered_product_ids = list(order.orderitem_set.values_list("product_id", flat=True))
        selected_main_products = set(Product.objects.filter(id__in=ordered_product_ids)
                             .values_list("product_id", flat=True))
        ordered_categories = list(ProductCategory.objects.filter(product_id__in=selected_main_products)
                                .values_list("category_id", flat=True))

        print(f"Is First Order: {is_first_order}, Ordered Product IDs: {ordered_product_ids}, Ordered Categories: {ordered_categories}")
        return order, is_first_order, selected_main_products, ordered_categories


    def is_coupon_applicable(self, coupon, is_first_order, ordered_product_ids, ordered_categories):
        """Checks if a coupon is applicable based on applicable_products, applicable_categories, or first order."""
        print(f"Checking applicability for coupon {coupon.id}")

        if coupon.is_first_order and is_first_order:
            print(f"Coupon {coupon.id} is applicable because it's a first order.")
            return True

        if coupon.applicable_products.filter(id__in=ordered_product_ids).exists():
            print(f"Coupon {coupon.id} is applicable based on applicable products.")
            return True

        if coupon.applicable_categories.filter(id__in=ordered_categories).exists():
            print(f"Coupon {coupon.id} is applicable based on applicable categories.")
            return True

        print(f"Coupon {coupon.id} is NOT applicable.")
        return False






class SingleCouponView(APIView):
    """API to fetch a single valid coupon by its ID with error handling."""

    def get(self, request, coupon_id):
        try:
            user = request.user  # Assuming authentication is enabled

            # Get order_id from request params
            order_id = request.query_params.get("order_id")
            print(f"Received request for single coupon. User: {user}, Coupon ID: {coupon_id}, Order ID: {order_id}")

            order, is_first_order, ordered_product_ids, ordered_categories = AvailableCouponsView().get_order_details(user, order_id)
            print(f"Order details fetched: {order}, Is First Order: {is_first_order}")
            print(f"Ordered Product IDs: {ordered_product_ids}, Ordered Categories: {ordered_categories}")

            coupon = get_object_or_404(
                Coupon,
                id=coupon_id,
                active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            )

            is_applicable = AvailableCouponsView().is_coupon_applicable(coupon, is_first_order, ordered_product_ids, ordered_categories)
            print(f"Coupon {coupon_id} applicability: {is_applicable}")

            serializer = CouponSerializer(coupon)
            coupon_data = serializer.data
            coupon_data["is_applicable"] = is_applicable  # Add applicability flag

            return Response(
                {"message": "Coupon retrieved successfully.", "coupon": coupon_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Error retrieving coupon {coupon_id}: {e}")
            return Response(
                {"error": "Something went wrong while retrieving the coupon.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


