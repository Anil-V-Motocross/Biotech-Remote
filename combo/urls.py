from django.urls import path
from .view.client_side_combo import combo_offer_list, combo_offer_detail
from .view.admin_side_combo import combo_offer_crud_operation

urlpatterns = [
    path('combo-offers/', combo_offer_list, name='combo-offer-list'),
    path('combo-offers/<int:pk>/', combo_offer_detail, name='combo-offer-detail'),
    path('adminCombo-offers/', combo_offer_crud_operation, name='combo-offer-crud'),
    path('adminCombo-offers/<int:pk>/', combo_offer_crud_operation, name='combo-offer-crud-detail'),
]