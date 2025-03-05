from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

@csrf_exempt
def carriers_list(request):
    url = "https://shipway.in/api/carriers"

    payload = {
   
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, json=payload, headers=headers)

        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON content
            data = response.json()  # Use .json() to parse JSON response          
            
            # Check if 'status' is Success and 'carrier_id' exists
            if data.get("status") == "success":
                couriers  = data.get("couriers", [])
                print("successsssssss-------------------------------------")
                if couriers:
                    # Search for a specific courier (for example, "Bluedart")
                    courier_name_to_find = "bluedart"  # You can modify this based on your need
                    
                    # Find the courier with the specified name
                    selected_courier = next((courier for courier in couriers if courier["courier_name"].lower() == courier_name_to_find.lower()), None)
                    print("selected -----------:", selected_courier)

                    if selected_courier:
                        # Save the ID of the found courier in the session
                        request.session['couriers'] = request.session.get('couriers', {})  # Initialize the session variable if not present
                        request.session['couriers'][selected_courier["courier_name"]] = selected_courier["id"]
                        print(f"Carrier ID for {courier_name_to_find} stored in session:", request.session['couriers'])
                        
                        
                        return JsonResponse({
                            "status": "success",
                            "message": f"Courier {courier_name_to_find} found and saved.",
                            "carrier_id": courier_id,
                            "courier_details": selected_courier
                        })
                    else:
                        return JsonResponse({
                            "status": "failure",
                            "message": f"Courier {courier_name_to_find} not found."
                        })
                else:
                    return JsonResponse({"status": "failure", "message": "No couriers found"})
            else:
                return JsonResponse({"status": "failure", "message": "API request failed: status not success"})
        else:
            return JsonResponse({"status": "failure", "message": f"API request failed with status code {response.status_code}"})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})