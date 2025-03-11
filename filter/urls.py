from django.urls import path
from .views import ProductFilterListView
from .dynamic_filters import DynamicFilterView

urlpatterns = [
    path('filters/', DynamicFilterView.as_view(), name='dynamic-filters'),
    path('productsFitler/', ProductFilterListView.as_view(), name='product-list-filter'),
]