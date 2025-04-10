from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from order.models import Order, DeliveryAddress, OrderStatus
import requests
import json
import os
from dotenv import load_dotenv
from django.conf import settings
import base64
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError


load_dotenv()
username = os.getenv('SHIPWAY_USERNAME')
password = os.getenv('SHIPWAY_PASSWORD')

auth_string = f"{username}:{password}"
auth_bytes = auth_string.encode('utf-8')
auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')



def push_order_to_shipway(order_id):
    print(f"[DEBUG] Starting push to Shipway for Order ID: {order_id}")
    
    try:
        order = Order.objects.get(order_id=order_id)
        shipping_address = DeliveryAddress.objects.get(order_id=order)
        
        # Prepare products data
        order_items = order.orderitem_set.all()
        print(f"[DEBUG] Found {len(order_items)} order items.")

        products = []

        with transaction.atomic():
            for item in order_items:
                product = item.product_id
                
                if product.stock < item.quantity:
                    raise ValidationError(
                        f"Not enough stock for product '{product.name}' (SKU: {product.sku}). "
                        f"Available: {product.stock}, Required: {item.quantity}"
                    )

                # Reduce stock
                product.stock -= item.quantity
                product.save(update_fields=["stock"])

                product_data = {
                    "product": item.product_id.name,
                    "price": str(item.selling_price),
                    "product_code": item.sku,
                    "hsn_code": item.hsn_code if item.hsn_code else "",
                    "product_quantity": str(item.quantity),
                    "discount": str(item.discount),
                }
                products.append(product_data)

        print(f"[DEBUG] Product payload: {products}")
        
        payment_type = 'P'
        if order.payment_method == 'Cash':
            payment_type = 'C'

        payload = {
            "order_id": str(order.order_id),
            "products": products,
            "payment_type": payment_type,
            "email": order.email,
            "shipping_firstname": shipping_address.first_name,
            "shipping_lastname": shipping_address.last_name,
            "shipping_phone": order.mobile,
            "shipping_address": shipping_address.address,
            "shipping_city": shipping_address.city,
            "shipping_state": shipping_address.state,
            "shipping_country": "India",
            "shipping_zipcode": str(shipping_address.pincode),
            "order_total": str(order.grand_total)
        }

        print(f"[DEBUG] Final payload: {json.dumps(payload, indent=2)}")

        url = "https://app.shipway.com/api/v2orders"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth_base64}'
        }

        print(f"[DEBUG] Sending request to Shipway...")

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        print(f"[DEBUG] Shipway response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            print("[SUCCESS] Order successfully pushed to Shipway.")
            return {"message": "Order successfully pushed to Shipway"}
        else:
            print("[ERROR] Shipway API Error.")
            return {"error": f"Shipway API error: {response.text}"}

    except Order.DoesNotExist:
        error_msg = f"Order with ID {order_id} not found."
        print(f"[ERROR] {error_msg}")
        return {"error": error_msg}

    except DeliveryAddress.DoesNotExist:
        error_msg = f"Delivery address not found for order {order_id}."
        print(f"[ERROR] {error_msg}")
        return {"error": error_msg}

    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return {"error": str(e)}



@api_view(['GET'])
@permission_classes([IsAuthenticated])   
@authentication_classes([JWTAuthentication])
def get_shipway_order_by_id(request, order_id):
    """
    Fetch order details from Shipway using the given order_id.
    """
    try:
        headers = {
            'Authorization': f'Basic {auth_base64}'
        }

        # API URL with query parameter
        url = "https://app.shipway.com/api/getorders"
        params = {
            'orderid': order_id
        }

        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            if data.get("success") == 1 and data.get("message"):
                order_info = data["message"][0]

                tracking_number = order_info.get("tracking_number")

                if tracking_number:
                    try:
                        # Fetch the order object
                        order_obj = get_object_or_404(Order, order_id=order_id)

                        # If tracking_id is not already set, update it
                        if not order_obj.tracking_id:
                            order_obj.tracking_id = tracking_number
                            order_obj.save()
                    except Exception as e:
                        return Response(
                            {"error": f"Failed to update tracking ID: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

                return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": f"Failed to fetch order from Shipway: {response.text}"},
                status=response.status_code
            )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])   
@authentication_classes([JWTAuthentication])
def cancel_shipway_orders(request):
    """
    Cancel orders in Shipway system. Only 'New' and 'Onhold' orders can be cancelled.
    Expects a list of order_ids in the request body.
    """
    try:
        order_ids = request.data.get('order_ids')
        if not order_ids or not isinstance(order_ids, list):
            return Response({"error": "Invalid or missing 'order_ids' field. It should be a list."},
                            status=status.HTTP_400_BAD_REQUEST)

        headers = {
            'Authorization': f'Basic {auth_base64}',
            'Content-Type': 'application/json'
        }

        successfully_cancelled = []
        failed_orders = []

        for order_id in order_ids:
            try:
                order = get_object_or_404(Order, order_id=order_id)

                # Check ownership or staff
                if request.user != order.customer_id and not request.user.is_staff:
                    failed_orders.append({"order_id": order_id, "error": "Permission denied."})
                    continue

                # Send cancel request to Shipway
                url = "https://app.shipway.com/api/Cancelorders/"
                payload = {
                    "order_ids": [order_id]
                }
                response = requests.post(url, headers=headers, data=json.dumps(payload))

                if response.status_code == 200:
                    # Create status entry in DB
                    OrderStatus.objects.create(order=order, status='CANCELLED', notes='Cancelled via Shipway API')
                    successfully_cancelled.append(order_id)
                else:
                    failed_orders.append({
                        "order_id": order_id,
                        "error": f"Shipway Error: {response.text}"
                    })

            except Order.DoesNotExist:
                failed_orders.append({"order_id": order_id, "error": "Order not found."})
            except Exception as e:
                failed_orders.append({"order_id": order_id, "error": str(e)})

        return Response({
            "success": successfully_cancelled,
            "failed": failed_orders
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   