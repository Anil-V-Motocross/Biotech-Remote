from .views import create_service_enquiry,get_service_enquiries
from .views import servicelist
from django.urls import path

urlpatterns = [
    path('service_enquiry/',create_service_enquiry, name='create_service_enquiry'),
    path('get_service_enquiries/',get_service_enquiries, name='get_service_enquiries'),

    path('service_list/',servicelist, name='servicelist'),

]