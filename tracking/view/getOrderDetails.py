import requests 
from django.http import JsonResponse

def get_order_details(order_id):
    url = "https://shipway.in/api/getOrderShipmentDetails/"

    payload = {
        "username": "biotechmaaliit@gmail.com",
        "password": "79f78cc05ab89b88bf9c325db2977b71",
        "order_id": order_id
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, json=payload, headers=headers)
        data = response.json()
        print("get order details -----:", data)
        
        if response.status_code == 200:
            if data.get("status") == "Success":
                shipment_status = data.get("response", {}).get("current_status", "No status available")
                return JsonResponse({
                    "status": "Success",
                    "shipment_status": shipment_status,
                    "tracking_url": data.get("response", {}).get("tracking_url", "No tracking URL")
                })
            else:
                return JsonResponse({
                    "status": "Failed",
                    "message": data.get("message", "Unknown failure reason."),
                    "response_data": data
                })
        else:
            return JsonResponse({
                "status": "Failed",
                "message": f"Request failed with status code {response.status_code}"
            })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Request error: {str(e)}"
        })
    except KeyError as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Missing key in response: {str(e)}",
            "response_data": data
        })
    except Exception as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Unexpected error: {str(e)}"
        })
    

# Success Response    
# get order details -----: {'status': 'Success', 'response': {'current_status': 'No Information Yet', 'current_status_code': 'NFI', 'carrier': 'Bluedart', 'from': None, 'to': None, 'customer_name': 'ANIL V', 'order_data': 'Biotechmaali order data - Tool ', 'pickup_date': None, 'time': None, 'awbno': 'OTID0008', 'tracking_url': 'https://s.shipway.in/123744052/OTID0008'}}