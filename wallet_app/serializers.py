from rest_framework import serializers
from wallet_app.models import *

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = ['id', 'account_no', 'ifsc_code', 'account_name', 'date_time']

class Platform_priceSerializers(serializers.ModelSerializer):
    class Meta:
        model=Platform_price
        fields='__all__'

class announcementSerializers(serializers.ModelSerializer):
    class Meta:
        model= Announcement
        fields='__all__'

class ExchangePriceSerialziers(serializers.ModelSerializer):
    class Meta:
        model=Exchange_price
        fields='__all__'

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposit
        fields = [ 'user', 'network', 'deposit_address', 'created_time', 'deposit_amount', 'transaction_id', 'status']

class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

#trnsaction_password-------

class TransactionPasswordSerializer(serializers.Serializer):
    create_password = serializers.CharField(min_length=6, max_length=6)
    confirm_password = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        if data['create_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        if not data['create_password'].isdigit():
            raise serializers.ValidationError("Password must be numerical.")
        return data

class ResetTransactionPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        if not data['new_password'].isdigit():
            raise serializers.ValidationError("Password must be numerical.")
        return data

#exchange
import random
from rest_framework import serializers
from .models import Exchange, Deposit, Network

class ExchangeSerializer(serializers.ModelSerializer):
    user_password = serializers.CharField(write_only=True, required=True)
    network_name = serializers.CharField(write_only=True, required=True)  # Network name is needed for validation

    class Meta:
        model = Exchange
        fields = ['id', 'amount', 'user', 'bank_account', 'network_name', 'trade_no', 'utr', 'time', 'status', 'user_password']
        read_only_fields = ['trade_no', 'utr', 'time', 'status', 'user']

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None

        user_password = attrs.get('user_password')
        network_name = attrs.get('network_name')
        amount = attrs.get('amount')

        # Validate transaction password
        if user is None or user.transaction_password != user_password:
            raise serializers.ValidationError("Invalid transaction password.")

        # Validate network and amount
        network = Network.objects.filter(name=network_name).first()
        if not network:
            raise serializers.ValidationError(f"Network '{network_name}' not found.")

        deposit = Deposit.objects.filter(user=user, network=network).order_by('-created_time').first()
        if not deposit or deposit.deposit_amount < amount:
            raise serializers.ValidationError(f"Insufficient balance or deposit not found for network '{network_name}'.")

        attrs['deposit'] = deposit  # Associate deposit with exchange

        return attrs

    def create(self, validated_data):
        validated_data.pop('user_password', None)
        validated_data.pop('network_name', None)  # Remove this as it's not a direct model field

        trade_no = f"TR{''.join(random.choices('0123456789', k=12))}"
        utr = f"UTR{''.join(random.choices('0123456789', k=12))}"
        validated_data['trade_no'] = trade_no
        validated_data['utr'] = utr

        exchange = Exchange.objects.create(**validated_data)
        return exchange

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Fetch the network name from the deposit
        network_name = instance.deposit.network.name if instance.deposit else None
        representation['network_name'] = network_name
        return representation







#withdraw
class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['wallet_address', 'amount', 'network', 'user', 'created_time', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace network_id with network_name
        representation['network'] = instance.network.name if instance.network else None
        return representation

    def validate(self, attrs):
        user = attrs.get('user')
        wallet_address = attrs.get('wallet_address')

        # Check if a withdrawal already exists for this user
        existing_withdrawal = Withdrawal.objects.filter(user=user).first()

        if existing_withdrawal:
            # Check if the wallet address is different from the existing one
            if wallet_address and wallet_address != existing_withdrawal.wallet_address:
                raise serializers.ValidationError("Cannot change the wallet address after the first withdrawal.")
            # Use the existing wallet address
            attrs['wallet_address'] = existing_withdrawal.wallet_address
        else:
            # Ensure a new wallet address is provided for the first withdrawal
            if not wallet_address:
                raise serializers.ValidationError("Wallet address is required for the first withdrawal.")

        return attrs


class WithdrawalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['wallet_address', 'amount', 'network', 'created_time', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Replace network_id with network_name
        representation['network'] = instance.network.name if instance.network else None
        return representation