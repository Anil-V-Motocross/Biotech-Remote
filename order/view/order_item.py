from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from order.models import OrderItem, Order
from rest_framework import serializers
import time
from account.models import User
from product.models import Product


import datetime
from django.db.models import Max

def generate_order_id():
    # Get the current date in YYYYMMDD format
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')

    # Prefix for the order_id
    prefix = "BM"

    # Get the highest existing order_id for today
    last_order = Order.objects.filter(date=today).aggregate(Max('order_id'))
    last_order_id = last_order['order_id__max']

    # Extract serial number from the last order_id if it exists
    if last_order_id:
        serial_number = int(last_order_id[-5:]) + 1
    else:
        serial_number = 1  # Start from 1 if no order exists today

    # Create the new order_id
    new_order_id = f"{prefix}{date_str}{serial_number:05d}"  # Serial number padded to 5 digits
    return new_order_id


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def order_item(request):
    if request.method == 'GET':
        required_permissions = [
            'order.view_orderitem'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        # get the order id from query param
        order_id = request.query_params.get('order_id')
        
        order_items = OrderItem.objects.filter(order_id=int(order_id)).all()

        serializer = OrderItemSerializer(order_items, many=True)
        data = {
            'order_items': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    

    if request.method == 'POST':
        required_permissions = [
            'order.add_orderitem'
        ]
        
        # Check if the user has permission
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = generate_order_id()
        # Get customer details
        customer = User.objects.get(id=request.user.id)
        order = {
            "order_id": order_id,
            "date": time.strftime("%Y-%m-%d"),
            "customer_id": customer.id,
            "customer_name": customer.first_name,
            "email": customer.email,
            "mobile": customer.mobile,
            "address": customer.address,
            "tracking_id": "0",
            "payment_method": "Not defined",
            "status": "Initiated"
        }
        
        # Serialize and save order
        order_serializer = OrderSerializer(data=order)
        if order_serializer.is_valid():
            order_instance = order_serializer.save()  # Save the order and get the instance
            order_id = order_instance.id  # Get the actual order ID from the saved instance
        else:
            return Response(data={'message': 'error', 'errors': order_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        order_items = request.data  # Request contains the items
        
        total_order_amount = 0  # Initialize a variable to keep track of the grand total
        items_to_save = []
        
        # Loop through the order items and calculate the total for each item
        for item in order_items:
            product = Product.objects.get(id=item['prod_id'])  # Get the product by prod_id
            
            quantity = item['quantity']
            price = float(product.price)  # Get the price of the product (convert to float for calculation)
            total = quantity * price  # Calculate the total price for this item
            
            # Prepare data to create OrderItem
            order_item_data = {
                'order_id': order_instance.id,  # Use the saved order instance's ID
                'product_id': product.id,
                'quantity': quantity,
                'price': price,
                'total': total
            }
            
            # Serialize and save order item
            serializer = OrderItemSerializer(data=order_item_data)
            if serializer.is_valid():
                serializer.save()
                items_to_save.append(serializer.data)
                total_order_amount += total  # Add this item's total to the grand total
            else:
                return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Now that all order items are saved, update the grand_total in the order
        order_instance.grand_total = total_order_amount # Set the grand total
        order_instance.save()  # Save the updated order instance
        
        data = {
            'order_details': order_serializer.data,
        }

        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_201_CREATED)

