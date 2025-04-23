import requests
import os
from django.core.mail import send_mail


import requests
import os

def send_sms_to_admin(order):
    phone = "91" + os.getenv('ADMIN_PHONE')
    print(f"📱 Sending SMS to: {phone}")
    print(f"🧾 Order ID: {order.id}")

    try:
        url = "https://control.msg91.com/api/v5/flow/"
        payload = {
            "template_id": "60ffda6d9c235f799241960f",  # Use your correct template ID
            "recipients": [{
                "mobiles": phone,
                "name": "Admin",
                "otp": 1234  # assuming this fits your template
            }]
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authkey": os.getenv("MSG91_AUTHKEY")
        }

        print("📤 Sending request to MSG91...")
        response = requests.post(url, json=payload, headers=headers)

        print(f"✅ SMS Response Code: {response.status_code}")
        print(f"✅ SMS Response Body: {response.text}")

        return True
    except Exception as e:
        print(f"❌ Error sending SMS: {e}")
        return False




# def send_admin_email(order):
#     subject = "New Order Placed"
#     message = f"A new order has been placed.\n\nOrder ID: {order.id}\nCustomer: {order.customer.name}\nAmount: ₹{order.total_amount}"
#     from_email = os.getenv('DEFAULT_FROM_EMAIL')
#     recipient_list = [os.getenv('ADMIN_EMAIL')]

#     try:
#         send_mail(subject, message, from_email, recipient_list)
#         return True
#     except Exception as e:
#         print("Email sending failed:", e)
#         return False
