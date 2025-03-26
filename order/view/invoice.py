# views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from order.models import Order, OrderItem, OrderStatus, DeliveryAddress
from django.conf import settings

class OrderInvoicePDFView(RetrieveAPIView):
    """
    Generate PDF invoice only for delivered orders
    """
    queryset = Order.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'order_id'

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        
        # Check if order is delivered
        if not self.is_order_delivered(order):
            raise PermissionDenied("Invoice can only be generated for delivered orders")
        
        order_items = OrderItem.objects.filter(order_id=order)
        delivery_address = DeliveryAddress.objects.filter(order_id=order).first()

        context = {
            'order': order,
            'order_items': order_items,
            'company': self.get_company_details(),
            'delivery_address': delivery_address,
            'STATIC_ROOT': settings.STATIC_ROOT,
            'amount_in_words': amount_to_words(order.grand_total)
        }

        html_string = render_to_string('invoice/invoice2.html', context)
        pdf_file = HTML(string=html_string).write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'invoice_{order.order_id}.pdf'
        return response

    def is_order_delivered(self, order):
        """Check if the latest status is DELIVERED"""
        latest_status = order.status_history.first()
        return latest_status and latest_status.status == 'DELIVERED'

    def get_company_details(self):
        """Hardcoded company details"""
        return {
            'name': 'Your Company Name',
            'address': '123 Business Street, Business City',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'zip_code': '560001',
            'phone': '(123) 456-7890',
            'email': 'info@yourcompany.com',
            'gstin': '22AAAAA0000A1Z5'
        }    

def amount_to_words(amount):
    """
    Convert a number to Indian Rupees amount in words, including paise.
    Example: 9100.75 -> "Nine Thousand One Hundred Rupees and Seventy-Five Paise Only"
    """
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
             "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", 
            "Seventy", "Eighty", "Ninety"]
    def convert_less_than_hundred(num):
        if num < 10:
            return units[num]
        elif num < 20:
            return teens[num - 10]
        else:
            return tens[num // 10] + (" " + units[num % 10] if num % 10 != 0 else "")
    
    def convert_less_than_thousand(num):
        if num < 100:
            return convert_less_than_hundred(num)
        hundred = units[num // 100] + " Hundred"
        remainder = num % 100
        if remainder:
            return hundred + " " + convert_less_than_hundred(remainder)
        return hundred

    if amount == 0:
        return "Zero Rupees Only"
    
    # Split into whole and decimal parts
    whole_part = int(amount)
    decimal_part = round((amount - whole_part) * 100)  # Convert to paise

    parts = []
    
    crore = whole_part // 10000000
    whole_part %= 10000000
    lakh = whole_part // 100000
    whole_part %= 100000
    thousand = whole_part // 1000
    whole_part %= 1000
    hundred = whole_part // 100
    remainder = whole_part % 100

    if crore:
        parts.append(convert_less_than_thousand(crore) + " Crore")
    if lakh:
        parts.append(convert_less_than_thousand(lakh) + " Lakh")
    if thousand:
        parts.append(convert_less_than_thousand(thousand) + " Thousand")
    if hundred:
        parts.append(units[hundred] + " Hundred")
    if remainder:
        parts.append(convert_less_than_hundred(remainder))

    words = " ".join(parts) + " Rupees" if parts else "Zero Rupees"

    # Handle decimal part (paise)
    if decimal_part:
        words += " and " + convert_less_than_hundred(decimal_part) + " Paise"

    return words + " Only"