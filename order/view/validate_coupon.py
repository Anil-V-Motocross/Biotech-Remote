from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from coupon.models import Coupon, CouponUsage
from order.models import Order, OrderItem
from django.utils.timezone import now
from product.models import Product, ProductCategory
from decimal import Decimal
from order.serializers import PlaceOrderSerializer, OrderItemSerializer


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([JWTAuthentication])
# def validate_coupon(request):
#     print("\n🚀 [START] Applying Coupon 🚀\n")

#     user = request.user
#     coupon_code = request.data.get('coupon_code')
#     selected_coupon_id = request.data.get('selected_coupon_id')
#     order_id = request.data.get('order_id') 

#     print(f"🔍 User: {user}")
#     print(f"🔍 Coupon Code: {coupon_code}")
#     print(f"🔍 Selected Coupon ID: {selected_coupon_id}")
#     print(f"🔍 Order ID: {order_id}")

#     try:
#         order = Order.objects.get(id=order_id, customer_id=user)
#         order_total = Decimal(order.grand_total)
#     except Order.DoesNotExist:
#         print("❌ Order not found")
#         return Response(data={'error': 'Order not found'}, status=status.HTTP_400_BAD_REQUEST)
    
#     # Check if order is a combo purchase
#     if order.is_combo_purchase:
#         print("❌ Coupon cannot be applied to a combo purchase.")
#         return Response(data={'error': 'Coupon cannot be applied to a combo purchase'}, status=status.HTTP_400_BAD_REQUEST)

#     print(f"🔍 Order Total: {order_total}")


#     # Get the coupon (either manually entered or selected)
#     try:
#         if coupon_code:
#             coupon = Coupon.objects.get(code=coupon_code, active=True)
#             print(f"✅ Coupon Found: {coupon}")
#         elif selected_coupon_id:
#             coupon = Coupon.objects.get(id=selected_coupon_id, active=True)
#             print(f"✅ Coupon Found: {coupon}")
#         else:
#             print("⚠️ No coupon code or ID provided!")
#             return Response({'error': 'Please enter or select a coupon'}, status=status.HTTP_400_BAD_REQUEST)
#     except Coupon.DoesNotExist:
#         print("❌ Coupon does not exist or is inactive")
#         return Response({'error': 'Invalid or inactive coupon'}, status=status.HTTP_400_BAD_REQUEST)

#     # Check if the coupon is valid based on the date
#     if not (coupon.start_date <= now() <= coupon.end_date):
#         print("❌ Coupon has expired")
#         return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)

#     # Check user usage limit
#     # user_usage_count = CouponUsage.objects.filter(user=user, coupon=coupon).count()
#     user_usage_count = CouponUsage.usage_count_for_user(user, coupon)
#     print(f"🔍 User Usage Count: {user_usage_count} / {coupon.user_limit}")

#     if user_usage_count >= coupon.user_limit:
#         print("❌ User has already used this coupon")
#         return Response({'error': 'You have already used this coupon the maximum number of times'}, status=status.HTTP_400_BAD_REQUEST)

#     # Get all product IDs from the order
#     product_ids = list(OrderItem.objects.filter(order_id=order).values_list('product_id', flat=True))

#     print(f"🔍 Extracted Product IDs from Order: {product_ids}")

#     # Fetch products and related main products
#     selected_products = Product.objects.filter(id__in=product_ids).select_related('product_id')
#     selected_main_products = set(product.product_id for product in selected_products)   
#     print(f"🔍 Selected Products: {selected_products}")
#     print(f"🔍 Extracted MainProduct IDs: {[product.product_id.id for product in selected_products]}")

#     applicable = False

#     applicable_categories = set()
#     selected_categories = set()

#     # Condition 1: Applicable Categories
#     if coupon.applicable_categories.exists():
#         applicable_categories = set(coupon.applicable_categories.values_list('id', flat=True))
        
#         # Fetch the categories of the selected products using ProductCategory
#         selected_categories = set(
#             ProductCategory.objects.filter(product_id__in=selected_main_products)
#             .values_list('category_id', flat=True)
#         )

#         print(f"🔍 Coupon Applicable Categories (IDs): {applicable_categories}")
#         print(f"🔍 Selected Product Categories (IDs): {selected_categories}")

#     if selected_categories & applicable_categories:
#         applicable = True
#         print("✅ Coupon is applicable based on categories")

#     # Condition 2: Applicable Products
#     elif coupon.applicable_products.exists():
#         applicable_products = set(coupon.applicable_products.all())

#         print(f"🔍 Coupon Applicable Products: {applicable_products}")
#         print(f"🔍 Selected Main Products: {selected_main_products}")

#         if selected_main_products & applicable_products:
#             applicable = True
#             print("✅ Coupon is applicable based on specific products")

#     # Condition 3: First Order Coupon
#     elif coupon.is_first_order:
#         if Order.objects.filter(customer_id=user).exists():
#             print("❌ User is not a first-time buyer")
#             return Response(data={'error': 'Coupon is only valid for first-time users'}, status=status.HTTP_400_BAD_REQUEST)
#         applicable = True
#         print("✅ Coupon is applicable for first order")

#     # If none of the conditions are met
#     if not applicable:
#         print("❌ Coupon is not applicable to selected products")
#         return Response(data={'error': 'Coupon is not valid for the selected products'}, status=status.HTTP_400_BAD_REQUEST)

#     # Check minimum purchase amount
#     if order_total < (coupon.minimum_order_value or 0):
#         print(f"❌ Order total ({order_total}) is below minimum ({coupon.minimum_order_value})")
#         return Response(data={'error': f'Minimum order value should be {coupon.minimum_order_value}'}, status=status.HTTP_400_BAD_REQUEST)

#     # Check stackable condition
#     if not coupon.is_stackable and CouponUsage.objects.filter(order=order).exists():
#         print("❌ Coupon cannot be combined with another coupon in the same order")
#         return Response(data={'error': 'A coupon has already been applied to this order'}, status=status.HTTP_400_BAD_REQUEST)
    
#     # Calculate discount
#     discount_amount = 0
#     if coupon.discount_type == 'FLAT':
#         discount_amount = min(order_total, coupon.discount_value)
#         print(f"✅ Flat Discount Applied: {discount_amount}")
#     elif coupon.discount_type == 'PERCENTAGE':
#         discount_amount = (coupon.discount_value / Decimal(100)) * order_total
#         if coupon.max_discount_value:
#             discount_amount = min(discount_amount, coupon.max_discount_value)
#         print(f"✅ Percentage Discount Applied: {discount_amount}")

#     # earlier_discount = order.total_discount
#     new_total = order_total - discount_amount
#     print(f"✅ New Order Total After Discount: {new_total}")

#     # # Save coupon usage
#     # coupon_usage, created = CouponUsage.objects.get_or_create(user=user, coupon=coupon)

#     # if not created:
#     #     coupon_usage.usage_count += 1
#     #     coupon_usage.save()
#     # else:
#     #     coupon_usage.usage_count = 1  
#     #     coupon_usage.save()        
#     # print("✅ Coupon usage saved in database")

#     print("\n🎉 [END] Coupon Applied Successfully 🎉\n")

#     # **🔹 Update Order Model**
    
#     order.coupon_applied = True
#     order.applied_coupon = coupon
#     order.coupon_discount = discount_amount
#     order.grand_total = new_total  
#     order.save()

#     print("✅ Order updated with applied coupon")    

#     order_serializer = PlaceOrderSerializer(order)
#     order_items = OrderItem.objects.filter(order_id=order.id)
#     order_items_serializer = OrderItemSerializer(order_items, many=True)

#     return Response(data={
#         'success': True,
#         'discount_amount': discount_amount,
#         'new_total': new_total,
#         'coupon_code': coupon.code,
#         'redemption_message': coupon.redemption_message or "Coupon applied successfully!",
#         'order': order_serializer.data,
#         'order_items': order_items_serializer.data
#     }, status=status.HTTP_200_OK)






@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def validate_coupon(request):
    print("\n🚀 [START] Applying Coupon 🚀\n")

    user = request.user
    coupon_code = request.data.get('coupon_code')
    selected_coupon_id = request.data.get('selected_coupon_id')
    order_id = request.data.get('order_id')

    print(f"🔍 User: {user}")
    print(f"🔍 Coupon Code: {coupon_code}")
    print(f"🔍 Selected Coupon ID: {selected_coupon_id}")
    print(f"🔍 Order ID: {order_id}")

    try:
        order = Order.objects.get(id=order_id, customer_id=user)
        latest_status_entry = order.status_history.order_by('-timestamp').first()

        if not latest_status_entry or latest_status_entry.status != 'INITIATED':
            print("❌ Coupon can only be applied to orders with status 'INITIATED'.")
            return Response({'error': 'Coupon can only be applied to orders in INITIATED status.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_total = Decimal(order.grand_total)
    except Order.DoesNotExist:
        print("❌ Order not found")
        return Response({'error': 'Order not found'}, status=status.HTTP_400_BAD_REQUEST)

    if order.is_combo_purchase:
        print("❌ Coupon cannot be applied to a combo purchase.")
        return Response({'error': 'Coupon cannot be applied to a combo purchase'}, status=status.HTTP_400_BAD_REQUEST)

    print(f"🔍 Order Total: {order_total}")

    # Remove previously applied coupon if any
    if order.coupon_applied and order.applied_coupon:
        print(f"🔄 Removing previously applied coupon: {order.applied_coupon.code}")
        order_total += Decimal(order.coupon_discount)  # Restore the discount amount
        order.coupon_applied = False
        order.applied_coupon = None
        order.coupon_discount = Decimal(0)
        order.grand_total = order_total
        order.save()

        print(f"🔍 Order Total after removing coupon : {order_total}")
    
    # Fetch the coupon (either manually entered or selected)
    try:
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
        elif selected_coupon_id:
            coupon = Coupon.objects.get(id=selected_coupon_id, active=True)
        else:
            print("⚠️ No coupon code or ID provided!")
            # return Response({'error': 'Please enter or select a coupon'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'error': 'Please enter or select a coupon',
                'success': False,
                'discount_amount': 0,
                'new_total': order_total,
                'coupon_code': None,
                'order': PlaceOrderSerializer(order).data,
                'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
            }, status=status.HTTP_400_BAD_REQUEST)
        print(f"✅ Coupon Found: {coupon}")
    except Coupon.DoesNotExist:
        print("❌ Coupon does not exist or is inactive")
        # return Response({'error': 'Invalid or inactive coupon'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': 'Invalid or inactive coupon',
            'discount_amount': 0,
            'new_total': order_total,
            'coupon_code': None,
            'order': PlaceOrderSerializer(order).data,
            'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)

    if not (coupon.start_date <= now() <= coupon.end_date):
        print("❌ Coupon has expired")
        # return Response({'error': 'Coupon has expired'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
                    'success': False,
                    'error': 'Coupon has expired',
                    'discount_amount': 0,
                    'new_total': order_total,
                    'coupon_code': None,
                    'order': PlaceOrderSerializer(order).data,
                    'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
                }, status=status.HTTP_400_BAD_REQUEST)
    user_usage_count = CouponUsage.usage_count_for_user(user, coupon)
    if user_usage_count >= coupon.user_limit:
        print("❌ User has already used this coupon the maximum number of times")
        # return Response({'error': 'You have already used this coupon the maximum number of times'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': 'You have already used this coupon the maximum number of times',
            'discount_amount': 0,
            'new_total': order_total,
            'coupon_code': None,
            'order': PlaceOrderSerializer(order).data,
            'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)

    product_ids = list(OrderItem.objects.filter(order_id=order).values_list('product_id', flat=True))
    selected_products = Product.objects.filter(id__in=product_ids).select_related('product_id')
    selected_main_products = set(product.product_id for product in selected_products)

    applicable = False

    # Check applicable categories
    applicable_categories = set(coupon.applicable_categories.values_list('id', flat=True)) if coupon.applicable_categories.exists() else set()
    selected_categories = set(ProductCategory.objects.filter(product_id__in=selected_main_products).values_list('category_id', flat=True))

    if selected_categories & applicable_categories:
        applicable = True
    elif coupon.applicable_products.exists() and selected_main_products & set(coupon.applicable_products.all()):
        applicable = True
    elif coupon.is_first_order and not Order.objects.filter(customer_id=user).exists():
        applicable = True

    if not applicable:
        print("❌ Coupon is not applicable to selected products")
        # return Response({'error': 'Coupon is not valid for the selected products'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': 'Coupon is not valid for the selected products',
            'discount_amount': 0,
            'new_total': order_total,
            'coupon_code': None,
            'order': PlaceOrderSerializer(order).data,
            'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)

    if order_total < Decimal(coupon.minimum_order_value or 0):
        print(f"❌ Order total ({order_total}) is below minimum ({coupon.minimum_order_value})")
        # return Response({'error': f'Minimum order value should be {coupon.minimum_order_value}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': f'Minimum order value should be {coupon.minimum_order_value}',
            'discount_amount': 0,
            'new_total': order_total,
            'coupon_code': None,
            'order': PlaceOrderSerializer(order).data,
            'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)

    if not coupon.is_stackable and CouponUsage.objects.filter(order=order).exists():
        print("❌ Coupon cannot be combined with another coupon in the same order")
        # return Response({'error': 'A coupon has already been applied to this order'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'error': 'A coupon has already been applied to this order',
            'discount_amount': 0,
            'new_total': order_total,
            'coupon_code': None,
            'order': PlaceOrderSerializer(order).data,
            'order_items': OrderItemSerializer(OrderItem.objects.filter(order_id=order.id), many=True).data
        }, status=status.HTTP_400_BAD_REQUEST)

    discount_amount = Decimal(0)
    if coupon.discount_type == 'FLAT':
        discount_amount =  coupon.max_discount_value
    elif coupon.discount_type == 'PERCENTAGE':
        discount_amount = (Decimal(coupon.discount_value) / Decimal(100)) * order_total
        if coupon.max_discount_value:
            discount_amount = min(discount_amount, Decimal(coupon.max_discount_value))

    print("   type   ", coupon.discount_type, "   amoout   ", discount_amount, " coupon   ", coupon.discount_value)
    new_total = order_total - discount_amount
    print(f"✅ New Order Total After Discount: {new_total}")

    # Update Order Model
    order.coupon_applied = True
    order.applied_coupon = coupon
    order.coupon_discount = discount_amount
    order.grand_total = new_total
    order.save()

    order_serializer = PlaceOrderSerializer(order)
    order_items = OrderItem.objects.filter(order_id=order.id)
    order_items_serializer = OrderItemSerializer(order_items, many=True)

    return Response({
        'success': True,
        'discount_amount': discount_amount,
        'new_total': new_total,
        'coupon_code': coupon.code,
        'redemption_message': coupon.redemption_message or "Coupon applied successfully!",
        'order': order_serializer.data,
        'order_items': order_items_serializer.data
    }, status=status.HTTP_200_OK)