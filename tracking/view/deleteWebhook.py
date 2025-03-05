import requests
from rest_framework.response import Response
import json

from rest_framework.decorators import api_view

@api_view(["POST"])
def delete_webhook(request):
    api_url = "https://shipway.in/api/delete_webhooks"

    payload = {
        "username": "biotechmaaliit@gmail.com",
        "password": "79f78cc05ab89b88bf9c325db2977b71"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()

        print("API Response:", json.dumps(response_data, indent=2))  # Console log response

        if response.status_code == 200 and response_data.get("status") == "success":
            return Response({
                "status": response_data.get("status", "failed"),
                "message": response_data.get("message", "Webhook deleted successfully."),
                "status_code": response_data.get("status_code", "200"),
            }, status=200)
        else:
            return Response({
                "status": response_data.get("status", "failed"),
                "message": response_data.get("message", "Invalid Inputs"),
                "status_code": response_data.get("status_code", "401"),
            }, status=400)

    except requests.exceptions.RequestException as e:
        return Response({
            "status": "failed",
            "message": f"Request error: {str(e)}",
            "status_code": "500"
        }, status=500)
    
    except json.JSONDecodeError:
        return Response({
            "status": "failed",
            "message": "Invalid JSON response from API",
            "status_code": "500"
        }, status=500)
