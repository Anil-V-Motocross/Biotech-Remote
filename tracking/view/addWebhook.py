import requests
from django.http import JsonResponse
from tracking.models import Webhook  # Ensure the model is correctly imported

# def add_webhook(username, password, callback_url, events):

def add_webhook(request):
    api_url = "https://shipway.in/api/addWebhooks"
    
    # payload = {
    #     "username": username,
    #     "password": password,
    #     "callback_url": callback_url,
    #     "events": events  # Example: "INT,OOD,DEL,UND,RTO,RTD"
    # }
    
    payload = {
        "username": "biotechmaaliit@gmail.com",
        "password": "79f78cc05ab89b88bf9c325db2977b71",
        "callback_url": "http://www.dev.back.biotechmaali.com:8000/tracking/webhook/shipway/",
        "events": "INT,OOD,DEL,UND,RTO,RTD"
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()
        print("Webhook response: ", data)
        
        if response.status_code == 200 and data.get("status") == "success":
            # Save webhook details in the database
            # webhook, created = Webhook.objects.get_or_create(
            #     url=callback_url,
            #     defaults={"is_active": True}
            # )
            # if not created:
            #     webhook.is_active = True  # Reactivate if it already exists
            #     webhook.save()
            
            return JsonResponse({
                "status": "Success",
                "message": "Webhook has been inserted successfully.",
                "response_data": data
            })
        else:
            return JsonResponse({
                "status": "Failed",
                "message": data.get("message", "Invalid Inputs"),
                "response_data": data
            })
    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Request error: {str(e)}"
        })
    except Exception as e:
        return JsonResponse({
            "status": "Failed",
            "message": f"Unexpected error: {str(e)}"
        })
    

# ************ RESPONSE ************
# Webhook response:  {'status': 'success', 'message': 'Webhooks has Inserted successfully', 'status_code': '200'}