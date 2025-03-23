from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.response import Response
from rest_framework import status
from account.permissions import DynamicPermission
from account.views.validate_user_profile import validate_user_profile
from order.models import Cart, OrderItem
from product.models import Product
from combo.models import ComboOffer
from coupon.models import Coupon
from order.view.util import generate_bmo_id
from order.serializers import PlaceOrderSerializer, OrderItemSerializer
import time
from account.models import User
from decimal import Decimal



@api_view(['POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def place_order(request):
    print("🔹 Received order request:", request.data)

    if request.method != 'POST':
        print("❌ Invalid request method")
        return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

    required_permissions = ['order.add_order']
    if not any(request.user.has_perm(perm) for perm in required_permissions):
        print("❌ Permission denied for user:", request.user.username)
        return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    # Validate user profile
    user_profile = validate_user_profile(request.user)
    print("✅ User profile validation result:", user_profile)

    if not user_profile.get('user_profile'):
        print("❌ User profile validation failed")
        return Response(data={
            'message': user_profile.get('message'),
            'profile_status': user_profile.get('profile_status'),
            'address_status': user_profile.get('address_status')
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate order source
    order_source = request.data.get('order_source')
    print("🔹 Order source:", order_source)

    if order_source not in ['product', 'cart', 'combo']:
        print("❌ Invalid order source:", order_source)
        return Response(data={'message': 'Invalid order source.'}, status=status.HTTP_400_BAD_REQUEST)

    order_items = []
    total_price, total_discount = 0, 0
    is_combo_purchase = False
    is_shop_the_look = False

    # ✅ Case 1: Single Product Purchase
    if order_source == 'product':
        product_id = request.data.get('prod_id')
        quantity = request.data.get('quantity')

        print(f"🔹 Product purchase: Product ID: {product_id}, Quantity: {quantity}")

        if not product_id or not quantity:
            print("❌ Product ID and quantity are required")
            return Response(data={'message': 'Product ID and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            print("❌ Product not found:", product_id)
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if product.stock < quantity:
            print("❌ Product out of stock:", product_id)
            return Response(data={'message': 'Product out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

        sale_price = float(product.selling_price)
        total = quantity * sale_price
        # discount = float(product.discount) * quantity
        discount_amount = (float(product.mrp) * float(product.discount) / 100) * quantity


        print(f"✅ Adding product to order: {product.name}, Total: {total}, Discount: {discount_amount}")

        order_items.append({
            'product_id': product_id,
            'sku': product.sku,
            'quantity': quantity,
            'selling_price': sale_price,
            'mrp': product.mrp,
            'discount': discount_amount,
            'total': total
        })

        total_price += total
        total_discount += discount_amount

    # ✅ Case 2: Cart Order
    elif order_source == 'cart':
        cart_items = Cart.objects.filter(user_id=request.user.id).all()
        print(f"🔹 Cart order: Found {len(cart_items)} items")

        if not cart_items:
            print("❌ Cart is empty")
            return Response(data={'message': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.product_id.stock < item.quantity:
                print(f"❌ Product {item.product_id.name} is out of stock.")
                return Response(data={'message': f'Product {item.product_id.name} is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

            sale_price = float(item.product_id.selling_price)
            total = item.quantity * sale_price
            # discount = float(item.product_id.discount) * item.quantity
            discount_amount = (float(item.product_id.mrp) * float(item.product_id.discount) / 100) * item.quantity


            order_items.append({
                'product_id': item.product_id.id,
                'sku': item.product_id.sku,
                'quantity': item.quantity,
                'selling_price': sale_price,
                'mrp': item.product_id.mrp,
                'discount': discount_amount,
                'total': total
            })

            total_price += total
            total_discount += discount_amount

    # ✅ Case 3: Combo Offer
    elif order_source == 'combo':
        combo_id = request.data.get('combo_id')
        print(f"🔹 Combo order: Combo ID: {combo_id}")

        if not combo_id:
            print("❌ Combo offer ID is required")
            return Response(data={'message': 'Combo offer ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        combo = ComboOffer.objects.filter(id=combo_id).first()
        if not combo:
            print("❌ Combo offer not found:", combo_id)
            return Response(data={'message': 'Combo offer not found.'}, status=status.HTTP_400_BAD_REQUEST)

        is_shop_the_look = combo.is_shop_the_look
        is_combo_purchase = True

        for combo_product in combo.products.all():
            print("Combo product Details  :",combo_product)

            sale_price = combo_product.selling_price
            # discount = combo_product.discount
            discount = (float(combo_product.mrp) * float(combo_product.discount) / 100) 

            total = sale_price

            print(f"✅ Adding combo product: {combo_product.name}, Total: {total}, Discount: {discount}")

            order_items.append({
                'product_id': combo_product.id,
                'sku': combo_product.sku,
                'quantity': 1,
                'selling_price': sale_price,
                'mrp': combo_product.mrp,
                'discount': discount,
                'total': total,
                'combo_offer': combo_id
            })

        total_price = combo.final_price
        total_discount = combo.discount

    # ✅ Generate Order ID & Fetch Customer
    order_id = generate_bmo_id()
    print("✅ Generated order ID:", order_id)

    customer = User.objects.filter(id=request.user.id).first()
    if not customer:
        print("❌ Customer not found")
        return Response(data={'message': 'Customer not found.'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Check Coupon Application (Only for non-combo orders)
    coupon_discount = 0
    applied_coupon = None
    if not is_combo_purchase:
        coupon_code = request.data.get('coupon_code')
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
            if coupon and total_price >= coupon.minimum_order_value:
                if coupon.discount_type == 'FLAT':
                    discount_amount = min(total_price, coupon.discount_value)
                elif coupon.discount_type == 'PERCENTAGE':
                    discount_amount = (coupon.discount_value / Decimal(100)) * total_price
                    if coupon.max_discount_value:
                        discount_amount = min(discount_amount, coupon.max_discount_value)
                coupon_discount = discount_amount
                applied_coupon = coupon
            else:
                return Response(data={'message': 'Invalid or ineligible coupon.'}, status=status.HTTP_400_BAD_REQUEST)

    grand_total = total_price - total_discount

    # ✅ Create and Save Order
    order_data = {
        "order_id": order_id,
        "date": time.strftime("%Y-%m-%d"),
        "customer_id": customer.id,
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
        "is_combo_purchase": is_combo_purchase,
        "is_shop_the_look": is_shop_the_look 
    }

    print("🔹 Order Data:", order_data)

    order_serializer = PlaceOrderSerializer(data=order_data)
    if order_serializer.is_valid():
        order_instance = order_serializer.save()
        print("✅ Order created successfully")
    else:
        print("❌ Order serialization error:", order_serializer.errors)
        return Response(data={'message': 'Error', 'errors': order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Save Order Items
    order_item_instances = []
    print("Order instance ID:", order_instance.id)  

    for item in order_items:
        # Assign the order_instance.id to order_id
        item['order_id'] = order_instance.id  # ✅ Correctly assign the order ID
        order_item_serializer = OrderItemSerializer(data=item)
        
        if order_item_serializer.is_valid():
            order_item_instance = order_item_serializer.save()
            order_item_instances.append(order_item_instance)  # Add the saved instance to the list
        else:
            print("❌ Order item error:", order_item_serializer.errors)
            return Response(data={'message': 'Error', 'errors': order_item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    print("✅ Order items created successfully")

    # ✅ Clear Cart
    if order_source == 'cart':
        Cart.objects.filter(user_id=request.user.id).delete()
        print("🛒 Cart cleared")

    # ✅ Return Order Details
    order_items_serializer = OrderItemSerializer(order_item_instances, many=True)

    return Response(data={
        'message': 'success',
        'data': {
            'order': order_serializer.data,
            'order_items': order_items_serializer.data
        }
    }, status=status.HTTP_200_OK)