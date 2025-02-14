from order.models import Order
import datetime
from django.db.models import Max

def generate_bmo_id():
    # Get the current date in YYYYMMDD format
    today = datetime.date.today()
    date_str = today.strftime('%Y%m%d')

    # Prefix for the order_id
    prefix = "BMO"

    # Get the highest existing order_id for today
    last_order = Order.objects.filter(date=today).aggregate(Max('order_id'))
    last_order_id = last_order['order_id__max']

    # Extract serial number from the last order_id if it exists
    if last_order_id:
        serial_number = int(last_order_id[-5:]) + 1
    else:
        serial_number = 1  # Start from 1 if no order exists today

    # Create the new order_id
    new_order_id = f"{prefix}{date_str}{serial_number:05d}"  # Serial number padded to 5 digits
    return new_order_id