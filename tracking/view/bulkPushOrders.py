import requests
from django.http import JsonResponse

def bulk_push_orders(request):
    url = "https://shipway.in/api/pushOrders"
    
    username = "biotechmaaliit@gmail.com"
    password = "79f78cc05ab89b88bf9c325db2977b71"
    
    shipments = [
        {
            "carrier_id": 1,
            "awb": "OTID0008",
            "order_id": "OOID0008",
            "first_name": "ANIL",
            "last_name": "V",
            "email": "anil@123.com",
            "phone": "+917012115234",
            "products": "FOP",
            "company": "Biotechmaali",
            "shipment_type": 1,
            "order_data": "Biotechmaali order data - Tool "
        },
        {
            "carrier_id": 2,
            "awb": "OTID0009",
            "order_id": "OOID0009",
            "first_name": "RAHUL",
            "last_name": "K",
            "email": "rahul@123.com",
            "phone": "+917012115235",
            "products": "ROP",
            "company": "AgroTech",
            "shipment_type": 2,
            "order_data": "AgroTech order data - seeds"
        },
        {
            "carrier_id": 2,
            "awb": "OTID0010",
            "order_id": "OOID0010",
            "first_name": "RAHUL",
            "last_name": "K",
            "email": "rahul@123.com",
            "phone": "+917012115235",
            "products": "ROP",
            "company": "AgroTech",
            "shipment_type": 2,
            "order_data": "AgroTech order data - Potss"
        }
    ]
    
    payload = {
        "username": username,
        "password": password,
        "shipments": shipments
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        print("bulk pushing --------:", data)
        
        if isinstance(data, list):
            success_count = sum(1 for order in data if order.get("status") == "Success")
            failure_count = len(data) - success_count
            return JsonResponse({
                "status": "Partial Success" if failure_count > 0 else "Success",
                "message": f"{success_count} orders succeeded, {failure_count} orders failed.",
                "response_data": data
            })
        
        if response.status_code == 200:
            if data.get("status") == "Success":
                return JsonResponse({
                    "status": "Success",
                    "message": data.get("msg", "Orders have been pushed successfully."),
                    "response_data": data
                })
            else:
                return JsonResponse({
                    "status": "Failed",
                    "message": data.get("msg", "Unknown failure reason."),
                    "response_data": data
                })
        else:
            return JsonResponse({
                "status": "Failed",
                "message": f"Request failed with status code {response.status_code}"
            })
    except Exception as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Error occurred: {str(e)}"
        })
