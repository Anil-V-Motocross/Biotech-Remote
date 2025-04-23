from django.urls import path
from .views import WalletDetailView, TransactionListView, create_wallet_order, verify_wallet_payment

urlpatterns = [
    path("wallet/", WalletDetailView.as_view(), name="walletdetail"),
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path('create-order/', create_wallet_order, name='create_wallet_order'),
    path('wallet/verify-payment/', verify_wallet_payment, name='verify_wallet_payment'),
]