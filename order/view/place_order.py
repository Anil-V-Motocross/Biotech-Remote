from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from account.views.validate_user_profile import validate_user_profile
from order.view.util import generate_bmo_id
from product.models import Product
from order.models import Cart
from order.models import Order
from account.models import User
import time
from rest_framework import serializers
from order.models import OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        
    # add main product name from to_representation
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_name'] = instance.product_id.product_id.name
        return representation

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

@api_view(['POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def place_order(request):
    if request.method == 'POST':
        required_permissions = [
            'order.add_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate user profile
        user_profile = validate_user_profile(request.user)
        if user_profile.get('user_profile') == False:
            return Response(data={'message': user_profile.get('message')}, status=status.HTTP_400_BAD_REQUEST)
        
        order_source = request.data.get('order_source')
        
        if not order_source:
            return Response(data={'message': 'Order source is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order_items = []
        
        if order_source == 'product':
            product_id = request.data.get('prod_id')
            quantity = request.data.get('quantity')
            if not product_id or not quantity:
                return Response(data={'message': 'Prod_id and quantity are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response(data={'message': 'Product not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
            stock = product.stock
            if stock < quantity:
                return Response(data={'message': 'Product out of stock.'}, status=status.HTTP_400_BAD_REQUEST)
            
            stock = product.stock
            if stock < quantity:
                stock_status = "Out Of Stock"
                sale_price = 0
            else:
                stock_status = "In Stock"
                
                sale_price = float(product.sale_price)  # Get the price of the product (convert to float for calculation)
            total = quantity * sale_price
            
            order_item = {
                'product_id': product_id,
                'sku': product.sku,
                'quantity': quantity,
                'sale_price': product.sale_price,
                'price': product.price,
                'discount': product.discount,
                'total': total,
                'stock_status': stock_status
            }
            
            order_items.append(order_item)
            
        elif order_source == 'cart':
            # check if user has items in cart
            if not Cart.objects.filter(user_id=request.user.id).exists():
                return Response(data={'message': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
            cart_items = Cart.objects.filter(user_id=request.user.id).all()
            
            if not cart_items:
                return Response(data={'message': 'No products found in order.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate total
            for item in cart_items:
                # add stock_status to the  order_items
                stock = item.product_id.stock
                if stock < item.quantity:
                    stock_status = "Out Of Stock"
                    sale_price = 0
                else:
                    stock_status = "In Stock"
                    
                    # Calculate price and total
                    quantity = item.quantity
                    sale_price = float(item.product_id.sale_price)  # Get the price of the product (convert to float for calculation)
                total = quantity * sale_price
                order_items.append({
                    'product_id': item.product_id.id,
                    'sku': item.product_id.sku,
                    'quantity': item.quantity,
                    'sale_price': sale_price,
                    'price': item.product_id.price,
                    'discount': item.product_id.discount,
                    'total': total,
                    'stock_status': stock_status
                })
            
        order_id = generate_bmo_id()
        # Get customer details
        customer = User.objects.get(id=request.user.id)
        
        if not customer:
            return Response(data={'message': 'Customer not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order
        order = {
            "order_id": order_id,
            "date": time.strftime("%Y-%m-%d"),
            "customer_id": customer.id,
            "customer_name": customer.first_name,
            "email": customer.email,
            "mobile": customer.mobile,
            "address": "Need  to create address",
            "tracking_id": "0",
            "status": "Initiated"
        }
        
        # Serialize and save order
        order_serializer = OrderSerializer(data=order)
        if order_serializer.is_valid():
            order_instance = order_serializer.save()  # Save the order and get the instance
            order_id = order_instance.id  # Get the actual order ID from the saved instance
            for item in order_items:
                order_item = {
                    "order_id": order_id,
                    "product_id": item["product_id"],
                    "sku": item["sku"],
                    "quantity": item["quantity"],
                    "sale_price": item["sale_price"],
                    "price": item["price"],
                    "discount": item["discount"],
                    "total": item["total"],
                    "stock_status": item["stock_status"]
                }
                order_item_serializer = OrderItemSerializer(data=order_item)
                if order_item_serializer.is_valid():
                    order_item_serializer.save()
                else:
                    return Response(data={'message': 'error', 'errors': order_item_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'message': 'error', 'errors': order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        
        # Calculate total = sum of price of order items, and discount = sum of discount of order items, total_amount = total - discount
        order_items = OrderItem.objects.filter(order_id=order_id).all()
        total_price = sum(item.total for item in order_items)
        total_discount = sum(item.discount for item in order_items)
        grand_total = total_price - total_discount
        
        # save from order instance
        order_instance.total_price = total_price
        order_instance.total_discount = total_discount
        order_instance.grand_total = grand_total
        order_instance.save()
        
        # Delete cart items
        if order_source == 'cart':
            Cart.objects.filter(user_id=request.user.id).delete()
            
        # Return order details and order items
        order_items = OrderItem.objects.filter(order_id=order_id).all()
        order_items_serializer = OrderItemSerializer(order_items, many=True)
        data = {
            "order": order_serializer.data,
            "order_items": order_items_serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)