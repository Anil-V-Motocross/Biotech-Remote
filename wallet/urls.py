from django.urls import path
from .views import WalletDetailView, TransactionListView

urlpatterns = [
    path("wallet/", WalletDetailView.as_view(), name="walletdetail"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
]