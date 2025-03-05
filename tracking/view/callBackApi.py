import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)

@csrf_exempt
def shipway_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            print("Webhook Data Received:", data)  # Console log
            logger.info(f"Webhook Data: {data}")  # Log the data

            return JsonResponse({"status": "success", "message": "Webhook received successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"status": "failed", "message": "Invalid JSON data."}, status=400)

    return JsonResponse({"status": "failed", "message": "Only POST requests are allowed."}, status=405)


#  **************** RESPONSE ********************
# Webhook Data Received: {'hash': '7d111ed3fefbdc00e52ccb2c91ed38f7', 'status_feed': [{'order_id': '99886000321149', 'awbno': '1348616939310', 'pickupdate': '2017-11-27 19:00:00', 'current_status_desc': 'Out for Delivery', 'current_status': 'OOD', 'from': 'GURGAON', 'to': 'BAHARAICH', 'status_time': '2017-12-09 13:41:00', 'scans': [{'time': '2017-12-09 13:41:00', 'status': 'Out for delivery', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-08 20:44:00', 'status': 'Asked for delay delivery on 2017-12-09', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-08 13:51:00', 'status': 'Out for delivery', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-04 22:04:00', 'status': 'Reattempt - As per NDR instructions', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-02 11:06:00', 'status': 'Asked for delay delivery on 2017-12-03', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-02 10:58:00', 'status': 'Out for delivery', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-01 19:16:00', 'status': 'Received at destination city', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-01 19:00:00', 'status': 'Consignment received at destination city', 'location': 'Bahraich_Kotwali_D (Uttar Pradesh)'}, {'time': '2017-12-01 08:32:00', 'status': 'Added to IST', 'location': 'Lucknow_Hub (Uttar Pradesh)'}, {'time': '2017-12-01 06:19:00', 'status': 'Bagged at PC', 'location': 'Lucknow_Hub (Uttar Pradesh)'}, {'time': '2017-12-01 03:55:00', 'status': 'Bag Incoming at PC', 'location': 'Lucknow_Hub (Uttar Pradesh)'}, {'time': '2017-12-01 02:22:00', 'status': 'IST received', 'location': 'Lucknow_Hub (Uttar Pradesh)'}, {'time': '2017-11-30 12:43:00', 'status': 'Added to IST', 'location': 'Delhi_Gateway_HB (Delhi)'}, {'time': '2017-11-30 06:54:00', 'status': 'IST received', 'location': 'Delhi_Gateway_HB (Delhi)'}, {'time': '2017-11-30 05:00:00', 'status': 'Consignment dispatched from origin city', 'location': 'Gurgaon_Bilaspur_HB (Haryana)'}]}]}