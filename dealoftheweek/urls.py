from django.urls import path
from .views import ActiveDealOfTheWeekView, DealOfTheWeekListCreateView, DealOfTheWeekDetailView

urlpatterns = [
    path('dealOfTheWeek/', ActiveDealOfTheWeekView.as_view(), name='deal-of-the-week'),
    path('adminDeals/', DealOfTheWeekListCreateView.as_view(), name='deals-list-create'),
    path('adminDeals/<int:pk>/', DealOfTheWeekDetailView.as_view(), name='deals-detail'),
]