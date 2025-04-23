import requests
import os
from dotenv import load_dotenv 

load_dotenv()

def send_order_sms_to_admin(order):
    admin_mobile = "91" + os.getenv("ADMIN_PHONE")  

    try:
        url = "https://control.msg91.com/api/v5/flow/"
        payload = {
            "template_id": "68073ae2d6fc05052f215793", 
            "recipients": [{
                "mobiles": admin_mobile,
                "var1": order.customer_name,
                "var2": order.order_id,
                "var3": order.date.strftime("%d-%m-%Y"),
            }]
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            # "authkey": "433172AwxmUdTOWK6746d6c2P1" 
            "authkey": os.getenv("MSG91_AUTHKEY")  
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send SMS to admin: {e}")
        return False
