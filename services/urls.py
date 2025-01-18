from .views import create_service_enquiry, get_service_enquiries, publicservicelist, servicelist

from django.urls import path

urlpatterns = [
    path('service_enquiry/',create_service_enquiry, name='create_service_enquiry'),
    path('get_service_enquiries/',get_service_enquiries, name='get_service_enquiries'),
    path('get_service_enquiries/<int:pk>/',get_service_enquiries,name='get_service_enquiries'),

    path('publicservice_list/',publicservicelist, name='publicservicelist'),
    path('servicelist/', servicelist, name='servicelist'),  # For list and create operations
    path('servicelist/<int:pk>/', servicelist, name='servicelist-detail'),
]