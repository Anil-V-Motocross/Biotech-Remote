from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

@csrf_exempt
def authenticate_user(request):
    url = "https://shipway.in/api/authenticateUser"

    payload = {
        "username": "biotechmaaliit@gmail.com",
        "password": "79f78cc05ab89b88bf9c325db2977b71"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "Success":
                request.session['user_id'] = data["user_id"]
                print("user_id:",request.session['user_id'])
                return JsonResponse({"status": "success", "message": "Authentication success"})
            else:
                return JsonResponse({"status": "failure", "message": "Authentication failed"})
        else:
            return JsonResponse({"status": "failure", "message": "API request failed"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
