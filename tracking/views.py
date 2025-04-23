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
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
import pgeocode
from .models import DeliveryLocation
from .serializers import PincodeCheckSerializer, BulkPincodeSerializer, DeliveryLocationSerializer
from account.permissions import IsStaffUser


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



# @api_view(['GET'])
# @permission_classes([IsAuthenticated])   
# @authentication_classes([JWTAuthentication])
# def get_shipway_order_by_id(request, order_id):
#     """
#     Fetch order details from Shipway using the given order_id.
#     """
#     try:
#         headers = {
#             'Authorization': f'Basic {auth_base64}'
#         }

#         # API URL with query parameter
#         url = "https://app.shipway.com/api/getorders"
#         params = {
#             'orderid': order_id
#         }

#         # Make the GET request
#         response = requests.get(url, headers=headers, params=params)

#         if response.status_code == 200:
#             data = response.json()

#             if data.get("success") == 1 and data.get("message"):
#                 order_info = data["message"][0]

#                 tracking_number = order_info.get("tracking_number")

#                 if tracking_number:
#                     try:
#                         # Fetch the order object
#                         order_obj = get_object_or_404(Order, order_id=order_id)

#                         # If tracking_id is not already set, update it
#                         if not order_obj.tracking_id:
#                             order_obj.tracking_id = tracking_number
#                             order_obj.save()
#                     except Exception as e:
#                         return Response(
#                             {"error": f"Failed to update tracking ID: {str(e)}"},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                         )

#                 return Response(data, status=status.HTTP_200_OK)
#         else:
#             return Response(
#                 {"error": f"Failed to fetch order from Shipway: {response.text}"},
#                 status=response.status_code
#             )

#     except Exception as e:
#         return Response(
#             {"error": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])   
@authentication_classes([JWTAuthentication])
def get_shipway_order_by_id(request, order_id):
    """
    Fetch order details from Shipway using the given order_id.
    Also updates tracking ID and order status history.
    """
    try:
        headers = {
            'Authorization': f'Basic {auth_base64}'
        }

        url = "https://app.shipway.com/api/getorders"
        params = {
            'orderid': order_id
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            if data.get("success") == 1 and data.get("message"):
                order_info = data["message"][0]
                tracking_number = order_info.get("tracking_number")
                shipment_status_scan = order_info.get("shipment_status_scan", [])

                order_obj = get_object_or_404(Order, order_id=order_id)

                # ✅ Update tracking ID if not already set
                if tracking_number and not order_obj.tracking_id:
                    order_obj.tracking_id = tracking_number
                    order_obj.save()

                # ✅ Define relevant statuses to save
                allowed_status_map = {
                    "Dispatched": "DISPATCHED",
                    "In Transit": "ON_THE_WAY",
                    "Out For Delivery": "OUT_FOR_DELIVERY",
                    "Delivered": "DELIVERED",
                }

                # ✅ Save only allowed shipment statuses
                for scan in shipment_status_scan:
                    raw_status = scan.get("status")
                    status_key = allowed_status_map.get(raw_status)

                    if status_key:
                        timestamp = scan.get("datetime")
                        notes = scan.get("sub_status", "")

                        # Prevent duplicates if needed
                        if not OrderStatus.objects.filter(order=order_obj, status=status_key, timestamp=timestamp).exists():
                            OrderStatus.objects.create(
                                order=order_obj,
                                status=status_key,
                                timestamp=timestamp,
                                notes=notes
                            )

                return Response(data, status=status.HTTP_200_OK)

            return Response(
                {"error": "Shipway response does not contain valid message"},
                status=status.HTTP_400_BAD_REQUEST
            )

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


def push_return_order_to_shipway(order_id):
    print(f"[DEBUG] Starting return push to Shipway for Order ID: {order_id}")

    try:
        order = Order.objects.get(order_id=order_id)
        shipping_address = DeliveryAddress.objects.get(order_id=order)
        order_items = order.orderitem_set.all()

        print(f"[DEBUG] Found {len(order_items)} order items for return.")

        products = []
        for item in order_items:
            product_data = {
                "product": item.product_id.name,
                "price": str(item.selling_price),
                "product_code": item.sku,
                "hsn_code": item.hsn_code or "",
                "product_quantity": str(item.quantity),
                "discount": str(item.discount),
            }
            products.append(product_data)

        payment_type = 'P' if order.payment_method != 'Cash' else 'C'

        return_order_status = "E"  
        return_reason_id = 1       
        # refund_payment_id = 1      
        # transfer_details = {
        #     "account_number": "1234567890",
        #     "ifsc_code": "SBIN0001234",
        #     "account_holder_name": "John Doe",
        #     "bank_name": "SBI"
        # }

        payload = {
            "order_id": str(order.order_id),
            "return_order_status": return_order_status,
            "return_reason_id": return_reason_id,
            # "refund_payment_id": refund_payment_id,
            # "transfer_details": transfer_details,
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

        print(f"[DEBUG] Return payload: {json.dumps(payload, indent=2)}")

        url = "https://app.shipway.com/api/Createreturns"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_base64}'  
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        print(f"[DEBUG] Shipway Return API response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            print("[SUCCESS] Return order successfully pushed to Shipway.")
            return {"message": "Return order successfully pushed to Shipway"}
        else:
            print("[ERROR] Shipway Return API Error.")
            return {"error": f"Shipway Return API error: {response.text}"}

    except Order.DoesNotExist:
        return {"error": f"Order with ID {order_id} not found."}
    except DeliveryAddress.DoesNotExist:
        return {"error": f"Delivery address not found for order {order_id}."}
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return {"error": str(e)}





class PincodeCheckAPIView(CreateAPIView):
    serializer_class = PincodeCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pincode = serializer.validated_data['pincode']

            try:
                # Fetch location details using pgeocode
                nomi = pgeocode.Nominatim('IN')
                location = nomi.query_postal_code(pincode)

                # If invalid or not found
                if location is None or location.place_name is None or not str(location.postal_code).isdigit():
                    return Response({'error': 'Invalid Pincode'}, status=status.HTTP_400_BAD_REQUEST)

                # Check delivery availability from DB
                is_available = DeliveryLocation.objects.filter(pincode=pincode).exists()

                data = {
                    'pincode': pincode,
                    # 'place_name': location.place_name,
                    'state': location.state_name,
                    'delivery_available': is_available
                }

                return Response(data, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({'error': 'Something went wrong while checking the pincode.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ****** Admin Api ******
class BulkPincodeCreateView(CreateAPIView):
    serializer_class = BulkPincodeSerializer
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pincodes = serializer.validated_data['pincodes']
            nomi = pgeocode.Nominatim('IN')

            added = []
            skipped = []
            invalid = []

            for pin in pincodes:
                location = nomi.query_postal_code(pin)

                if location is None or location.place_name is None or not str(location.postal_code).isdigit():
                    invalid.append(pin)
                    continue

                obj, created = DeliveryLocation.objects.get_or_create(
                    pincode=pin,
                    defaults={
                        'city': location.place_name,
                        'state': location.state_name
                    }
                )
                if created:
                    added.append(pin)
                else:
                    skipped.append(pin)

            return Response({
                "added": added,
                "skipped_already_exists": skipped,
                "invalid_pincodes": invalid
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List all pincodes with created time
class PincodeListView(ListAPIView):
    queryset = DeliveryLocation.objects.all().order_by('-created_at')
    serializer_class = DeliveryLocationSerializer
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]


# Delete multiple pincodes
class BulkPincodeDeleteView(DestroyAPIView):
    serializer_class = BulkPincodeSerializer
    permission_classes = [IsStaffUser]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pincodes = serializer.validated_data['pincodes']
            deleted = []
            not_found = []

            for pin in pincodes:
                try:
                    obj = DeliveryLocation.objects.get(pincode=pin)
                    obj.delete()
                    deleted.append(pin)
                except DeliveryLocation.DoesNotExist:
                    not_found.append(pin)

            return Response({
                "deleted": deleted,
                "not_found": not_found
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)