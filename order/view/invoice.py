# views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.generics import RetrieveAPIView
from rest_framework.exceptions import PermissionDenied
from order.models import Order, OrderItem, OrderStatus

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
        context = {
            'order': order,
            'order_items': order_items,
            'company': self.get_company_details()
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