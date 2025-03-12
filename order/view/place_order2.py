from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.response import Response
from rest_framework import status
from account.permissions import DynamicPermission
from account.views import validate_user_profile
from order.models import Cart, OrderItem
from product.models import Product
from combo.models import ComboOffer
from coupon.models import Coupon
from order.view.util import generate_bmo_id
from order.serializers import PlaceOrderSerializer, OrderItemSerializer
import time

@api_view(['POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def place_order(request):
    if request.method != 'POST':
        return Response(data={'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

    required_permissions = ['order.add_order']
    if not any(request.user.has_perm(perm) for perm in required_permissions):
        return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    # Validate user profile
    user_profile = validate_user_profile(request.user)
    if not user_profile.get('user_profile'):
        return Response({
            'message': user_profile.get('message'), 
            'profile_status': user_profile.get('profile_status'),
            'address_status': user_profile.get('address_status')
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate order source
    order_source = request.data.get('order_source')
    if order_source not in ['product', 'cart', 'combo']:
        return Response(data={'message': 'Invalid order source.'}, status=status.HTTP_400_BAD_REQUEST)

    order_items = []
    total_price, total_discount = 0, 0  # Order total calculations
    is_combo_purchase = False

    # ✅ Case 1: Single Product Purchase
    if order_source == 'product':
        product_id = request.data.get('prod_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response(data={'message': 'Product ID and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if product.stock < quantity:
            return Response(data={'message': 'Product out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

        sale_price = float(product.sale_price)
        total = quantity * sale_price
        discount = float(product.discount) * quantity

        order_items.append({
            'product_id': product_id,
            'sku': product.sku,
            'quantity': quantity,
            'sale_price': sale_price,
            'price': product.price,
            'discount': discount,
            'total': total
        })

        total_price += total
        total_discount += discount

    # ✅ Case 2: Cart Order
    elif order_source == 'cart':
        cart_items = Cart.objects.filter(user_id=request.user.id).all()
        if not cart_items:
            return Response(data={'message': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.product_id.stock < item.quantity:
                return Response(data={'message': f'Product {item.product_id.name} is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

            sale_price = float(item.product_id.sale_price)
            total = item.quantity * sale_price
            discount = float(item.product_id.discount) * item.quantity

            order_items.append({
                'product_id': item.product_id.id,
                'sku': item.product_id.sku,
                'quantity': item.quantity,
                'sale_price': sale_price,
                'price': item.product_id.price,
                'discount': discount,
                'total': total
            })

            total_price += total
            total_discount += discount

    # ✅ Case 3: Combo Offer Order (Only Combo Offer in Order)
    elif order_source == 'combo':
        combo_id = request.data.get('combo_id')
        if not combo_id:
            return Response(data={'message': 'Combo offer ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        combo = ComboOffer.objects.filter(id=combo_id).first()
        if not combo:
            return Response(data={'message': 'Combo offer not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Store each product in the combo as an order item
        for combo_product in combo.products.all():
            sale_price = combo_product.sale_price
            discount = combo_product.discount
            total = sale_price

            order_items.append({
                'product_id': combo_product.id,
                'sku': combo_product.sku,
                'quantity': 1,
                'sale_price': sale_price,
                'price': combo_product.price,
                'discount': discount,
                'total': total,
                'combo_offer': combo_id
            })

            total_price += total
            total_discount += discount

        is_combo_purchase = True

    # ✅ Generate Order ID & Fetch Customer
    order_id = generate_bmo_id()
    customer = request.user

    # ✅ Check Coupon Application (Only for non-combo orders)
    coupon_discount = 0
    applied_coupon = None
    if not is_combo_purchase:
        coupon_code = request.data.get('coupon_code')
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
            if coupon and total_price >= coupon.minimum_order_value:
                coupon_discount = coupon.discount_amount
                applied_coupon = coupon
            else:
                return Response(data={'message': 'Invalid or ineligible coupon.'}, status=status.HTTP_400_BAD_REQUEST)

    grand_total = total_price - total_discount - coupon_discount

    # ✅ Create and Save Order
    order_data = {
        "order_id": order_id,
        "date": time.strftime("%Y-%m-%d"),
        "customer": customer,
        "customer_name": customer.first_name,
        "email": customer.email,
        "mobile": customer.mobile,
        "total_price": total_price,
        "total_discount": total_discount,
        "coupon_applied": bool(coupon_discount > 0),
        "applied_coupon": applied_coupon.id if applied_coupon else None,
        "coupon_discount": coupon_discount,
        "grand_total": grand_total,
        "status": "Initiated",
        "is_combo_purchase": is_combo_purchase
    }

    order_serializer = PlaceOrderSerializer(data=order_data)
    if order_serializer.is_valid():
        order_instance = order_serializer.save()
    else:
        return Response(data={'message': 'Error', 'errors': order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save Order Items
    for item in order_items:
        item['order'] = order_instance.id
        order_item_serializer = OrderItemSerializer(data=item)
        if order_item_serializer.is_valid():
            order_item_serializer.save()
        else:
            return Response(data={'message': 'Error', 'errors': order_item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Clear Cart if Order was from Cart
    if order_source == 'cart':
        Cart.objects.filter(user_id=request.user.id).delete()

    # ✅ Return Order Details
    order_items = OrderItem.objects.filter(order=order_instance).all()
    order_items_serializer = OrderItemSerializer(order_items, many=True)

    return Response(data={
        'message': 'Order placed successfully.',
        'order': order_serializer.data,
        'order_items': order_items_serializer.data
    }, status=status.HTTP_200_OK)
