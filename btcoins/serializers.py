from rest_framework import serializers
from .models import BTCoinsWallet, BTCoinsTransaction, BTCoinsSettings

class BTCoinsWalletSerializer(serializers.ModelSerializer):
    total_referrals  = serializers.IntegerField(source='referral_used_count', read_only=True)
    class Meta:
        model = BTCoinsWallet
        fields = ['total_coins', 'referral_code', 'total_referrals']


class BTCoinsTransactionSerializer(serializers.ModelSerializer):
    """ Serializer for BTCoinsTransaction model """

    class Meta:
        model = BTCoinsTransaction
        fields = [
            "id",
            "coins",
            "transaction_type",
            "reference",
            "created_at",
            # "expires_at",
            # "notified",
        ]        


class BTCoinsSettingsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BTCoinsSettings
        fields = '__all__'        