from django.urls import path
from .view.client_side_combo import combo_offer_list, combo_offer_detail

urlpatterns = [
    path('combo-offers/', combo_offer_list, name='combo-offer-list'),
    path('combo-offers/<int:pk>/', combo_offer_detail, name='combo-offer-detail'),
]