import requests
from django.http import JsonResponse

def push_order_data(order):
    url = "https://shipway.in/api/PushOrderData" 

    payload ={
        "username": "biotechmaaliit@gmail.com",
        "password": "79f78cc05ab89b88bf9c325db2977b71",
        "carrier_id": 1,
        "awb": order.tracking_id, #tracking_id
        "order_id": order.order_id,
        "first_name":order.customer_name,
        "last_name": " ",
        "email": order.email,
        "phone": order.mobile,
        "products": "First order product description",
        "company": "Biotechmaali",
        "shipment_type": 1,
        "order_data": "Biotechmaali order data - plant type"

    }
    
    # payload ={
    #     "username": "biotechmaaliit@gmail.com",
    #     "password": "79f78cc05ab89b88bf9c325db2977b71",
    #     "carrier_id": 1,
    #     "awb": "OTID0001", #tracking_id
    #     "order_id": "OOID0001",
    #     "first_name":"ANIL",
    #     "last_name": "V",
    #     "email": "anil@123.com",
    #     "phone": "+917012115234",
    #     "products": "First order product description",
    #     "company": "Biotechmaali",
    #     "shipment_type": 1,
    #     "order_data": "Biotechmaali order data - plant type"

    # }

    headers = {
        "Content-Type":"application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    
    try:
        # Send the request to the API
        response = requests.post(url, json=payload, headers=headers)

        # Check if the response was successful
        if response.status_code == 200:
            data = response.json()
            print("Push Order Data - Success", data)

            # Check for the response status and handle different cases
            if data.get("status") == "Success":
                return JsonResponse({
                    "status": "Success",
                    "message": data.get("msg", "Order has been pushed successfully.")
                })

            elif data.get("status") == "Failed":
                return JsonResponse({
                    "status": "Failed",
                    "message": data.get("msg", "Unknown failure reason.")
                })

            else:
                return JsonResponse({
                    "status": "Failed",
                    "message": "Unexpected status in response."
                })

        else:
            return JsonResponse({
                "status": "Failed",
                "message": f"Request failed with status code {response.status_code}"
            })

    except Exception as e:
        # Catch any exception and return a meaningful message
        return JsonResponse({
            "status": "Failed",
            "message": f"Error occurred: {str(e)}"
        })