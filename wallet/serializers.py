from rest_framework import serializers
from .models import Wallet, Transaction

from rest_framework import serializers
from .models import Wallet, Transaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [ "balance", "created_at", "updated_at"]

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ["transaction_type", "amount", 
                  "status", "reference_id", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


