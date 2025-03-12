from django.urls import path
from .view.franchise import franchise
from .view.franchise_enquiry import FranchiseEnquiryCreateAPIView

app_name = 'franchise'

urlpatterns = [
    path('', franchise, name='franchise'),
    path('<int:pk>/', franchise, name='franchise'),
    path('add_franchise/',FranchiseEnquiryCreateAPIView.as_view(), name='create-franchise')
]