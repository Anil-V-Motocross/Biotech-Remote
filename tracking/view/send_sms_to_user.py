import requests
import os
from dotenv import load_dotenv 

load_dotenv()

def send_order_confirmation_sms_to_admin(order, status):
    mobile = "91" + str(order.mobile)
    print("started sending msg to the user\n mobile:",mobile)

    if status == 'ORDER_CONFIRMED':
        template_id = "68073b76d6fc0570dc5f2932"    
        recipients = {
                "mobiles": mobile,
                "var1": order.customer_name,
                "var2": order.order_id,           
            }
    elif status == 'READY_FOR_PICKUP':
        template_id = "68073c48d6fc05337f2264d2"
        recipients = {
                "mobiles": mobile,
                "var1": order.customer_name,
                "var2": order.order_id,  
                "var3": order.store_id.location         
            }
        
    try:
        url = "https://control.msg91.com/api/v5/flow/"
        payload = {
            "template_id": template_id, 
            "recipients" : [recipients]
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": os.getenv("MSG91_AUTHKEY")  
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send SMS to admin: {e}")
        return False
