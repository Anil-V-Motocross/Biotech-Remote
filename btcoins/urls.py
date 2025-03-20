from django.urls import path
from .views import UserWalletView, UserTransactionsView, BTCoinsSettingsView

urlpatterns = [
    path('btcoinswallet/', UserWalletView.as_view(), name='user_btcoinsWallet'),
    path('btcoinsTransactions/', UserTransactionsView.as_view(), name='user_btcoinsTransactions'),
    path('adminBtcoinsSettings/', BTCoinsSettingsView.as_view(), name='btcoins-settings'),
]