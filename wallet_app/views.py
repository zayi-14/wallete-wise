from django.shortcuts import render
from rest_framework import generics,permissions
# from rest_framework.views import APIView
from wallet_app.models import *
from wallet_app.serializers import *
from django.http import Http404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from wallet_app.models import BankDetails
from rest_framework.permissions import IsAuthenticated,AllowAny
import random
import string
from django.shortcuts import render, redirect, get_object_or_404



class BankDetailsManageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankDetailsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bank_detail = serializer.save(user=request.user)  # Associate with the authenticated user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        bank_detail = BankDetails.objects.get(user=request.user)
        serializer = self.get_serializer(bank_detail, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    def get(self, request, *args, **kwargs):
        """
        List all bank details associated with the authenticated user.
        """
        bank_details = BankDetails.objects.filter(user=request.user)  # Get all bank details for the user
        serializer = self.get_serializer(bank_details, many=True)  # Serialize the queryset
        return Response(serializer.data, status=status.HTTP_200_OK)


class BankDetailsUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankDetailsSerializer

    def get_object(self):
        """
        This method gets the bank details object based on the `id` provided
        and ensures it belongs to the authenticated user.
        """
        user = self.request.user
        bank_detail_id = self.kwargs.get('id')
        try:
            # Ensure the bank detail belongs to the authenticated user
            bank_detail = BankDetails.objects.get(id=bank_detail_id, user=user)
            return bank_detail
        except BankDetails.DoesNotExist:
            raise Http404("Bank details not found or not owned by the user")

    def put(self, request, *args, **kwargs):
        """
        Handle PUT request to update bank details.
        """
        bank_detail = self.get_object()
        serializer = self.get_serializer(bank_detail, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BankDetailsDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankDetailsSerializer

    def get_object(self):
        """
        This method gets the bank details object based on the `id` provided
        and ensures it belongs to the authenticated user.
        """
        user = self.request.user
        bank_detail_id = self.kwargs.get('id')
        try:
            # Ensure the bank detail belongs to the authenticated user
            bank_detail = BankDetails.objects.get(id=bank_detail_id, user=user)
            return bank_detail
        except BankDetails.DoesNotExist:
            raise Http404("Bank details not found or not owned by the user")

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE request to delete bank details.
        """
        bank_detail = self.get_object()
        self.perform_destroy(bank_detail)
        return Response(status=status.HTTP_204_NO_CONTENT)





class Platform_pricelist(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class=Platform_priceSerializers
    queryset=Platform_price.objects.all()

class announcementlist(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    queryset=Announcement.objects.all()
    serializer_class=announcementSerializers    

class Exchange_pricelist(generics.ListAPIView):
    permission_classes=[permissions.AllowAny]
    queryset=Exchange_price.objects.all()
    serializer_class=ExchangePriceSerialziers




# views.py
# views.py
import re
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from twilio.rest import Client
import random
from django.contrib.auth import get_user_model
from wallet_app.models import OTP
from wallet_app.serializers import OTPRequestSerializer

User = get_user_model()

# Initialize Twilio client with actual credentials
twilio_client = Client('AC3fa4bde9b30f960214e1452787cb5d51', 'd5df84653e51e7434fdaae5cb74eeaed')

otp_storage = {}

def send_otp(mobile):
    otp = random.randint(100000, 999999)
    otp_storage[mobile] = otp
    OTP.objects.create(phone=mobile, otp=otp)
    try:
        message = twilio_client.messages.create(
            body=f'Your OTP is {otp}',
            from_='+15703540855',
            to=mobile
        )
    except Exception as e:
        print(f"Twilio Error: {e}")
        raise e
    return message.sid

class LoginRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('mobile')
        if not mobile:
            return Response({'mobile': 'Mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate mobile number format
        if not re.match(r'^\+\d{10,15}$', mobile):
            return Response({'error': 'Invalid mobile number format. Use the format: +1234567890'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(mobile=mobile)
            send_otp(mobile)
            return Response({'message': 'OTP sent to existing user'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            send_otp(mobile)
            return Response({'message': 'OTP sent for registration'}, status=status.HTTP_200_OK)

class VerifyOtpAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        if not mobile or not otp:
            return Response({'error': 'Mobile number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_storage.get(mobile) == int(otp):
            user, created = User.objects.get_or_create(mobile=mobile)
            if created:
                user.set_password(User.objects.make_random_password())
                user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class ResendOtpAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('mobile')
        if not mobile:
            return Response({'error': 'Mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)

        send_otp(mobile)
        return Response({'message': 'OTP resent'}, status=status.HTTP_200_OK)

class OTPAutofillView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp_instance = OTP.objects.filter(phone=phone).order_by('-created_at').first()
            if otp_instance:
                return Response({'otp': otp_instance.otp}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'No OTP found for this phone number'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract access and refresh tokens from the request
            access_token = None
            refresh_token = None

            # Check if tokens are present in cookies
            access_token = request.COOKIES.get('access_token')
            refresh_token = request.COOKIES.get('refresh_token')

            if not access_token:
                # If no access token in cookies, try to extract it from the auth header
                auth_header = request.headers.get('Authorization', '').split()
                if len(auth_header) == 2 and auth_header[0].lower() == 'Bearer':
                    access_token = auth_header[1]

            if not refresh_token:
                # If no refresh token in cookies, try to extract it from the request body
                refresh_token = request.data.get('refresh_token')

            # Blacklist the access token if present
            if access_token:
                try:
                    token = AccessToken(access_token)
                    token.blacklist()
                except Exception as e:
                    return Response({"error": f"Failed to blacklist access token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token if present
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    return Response({"error": f"Failed to blacklist refresh token: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



#deposite

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from wallet_app.models import Network, Address, Deposit,User
from .serializers import DepositSerializer
import random


class ChooseNetworkAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        networks = Network.objects.all()
        return Response({'networks': [network.name for network in networks]})

class GetDepositAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        network_name = request.data.get('network')
        network = get_object_or_404(Network, name=network_name)
        addresses = Address.objects.filter(network=network)
        
        if not addresses.exists():
            return Response({'error': 'No deposit addresses available for the selected network.'}, status=status.HTTP_404_NOT_FOUND)
        
        deposit_address = random.choice(addresses).deposit_address
        request.session['selected_network'] = network_name
        request.session['deposit_address'] = deposit_address
        return Response({'deposit_address': deposit_address})



class EnterDepositAmountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        deposit_amount = request.data.get('deposit_amount')
        deposit_address_value = request.data.get('deposit_address')

        if not deposit_amount or not deposit_address_value:
            return Response({'error': 'Please provide both deposit amount and deposit address.'}, status=status.HTTP_400_BAD_REQUEST)

        deposit_address = Address.objects.filter(deposit_address=deposit_address_value).first()

        if not deposit_address:
            return Response({'error': 'The provided deposit address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        network = deposit_address.network

        transaction_id = self.generate_transaction_id()

        deposit = Deposit.objects.create(
            user=request.user,  
            network=network,  
            deposit_address=deposit_address, 
            deposit_amount=deposit_amount,
            transaction_id=transaction_id
        )

        response_data = {
            'network': network.name,
            'deposit_address': deposit_address_value,
            'deposit_amount': deposit_amount,
            'transaction_id': transaction_id,
            'created_time': deposit.created_time
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        latest_deposit = Deposit.objects.filter(user=user).order_by('-created_time').first()
        
        if not latest_deposit:
            return Response({'error': 'No deposits found'}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            'deposit_amount': latest_deposit.deposit_amount,
            'deposit_address': latest_deposit.deposit_address.deposit_address,
            'network': latest_deposit.network.name,
            'transaction_id': latest_deposit.transaction_id,
            'created_time': latest_deposit.created_time
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def generate_transaction_id(self):
        return f"Tc{''.join(random.choices('0123456789', k=18))}"


    
class DepositHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        deposits = Deposit.objects.filter(user=user).order_by('-created_time')
        
        history = []
        for deposit in deposits:
            history.append({
                'network': deposit.network.name,
                'deposit_address': deposit.deposit_address.deposit_address,
                'created_time': deposit.created_time,
                'status': deposit.status,
                'deposit_amount': deposit.deposit_amount,
                'transaction_id': deposit.transaction_id,
            })
        
        return Response({'history': history}, status=status.HTTP_200_OK)    


from decimal import Decimal
from django.db.models import Sum
class AvailableBalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Sum of completed deposits
        total_deposits = Deposit.objects.filter(user=user, status='completed').aggregate(total=Sum('deposit_amount'))['total'] or Decimal('0.00')

        # Sum of completed exchanges
        total_exchanges = Exchange.objects.filter(user=user, status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Sum of completed withdrawals
        total_withdrawals = Withdrawal.objects.filter(user=user, status='completed').aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calculate available balance
        available_balance = total_deposits - total_exchanges - total_withdrawals

        return Response({'available_balance': str(available_balance)}, status=status.HTTP_200_OK)


#transaction password set up+_______________________________________

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class SetTransactionPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        create_password = request.data.get('create_password')
        confirm_password = request.data.get('confirm_password')

        # Validate that both fields are provided
        if not create_password or not confirm_password:
            return Response({
    'create_password': 'create a password',
    'confirm_password': 'confirm your password'
}
, status=status.HTTP_400_BAD_REQUEST)

        # Check if passwords match
        if create_password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the password is numeric and six digits
        if not (create_password.isdigit() and len(create_password) == 6):
            return Response({'error': 'Password must be a six-digit numeric value'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user already has a transaction password
        if hasattr(user, 'transaction_password') and user.transaction_password:
            return Response({'error': 'Transaction password is already set'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new transaction password
        user.transaction_password = create_password
        user.save()

        return Response({'message': 'Transaction password set successfully'}, status=status.HTTP_200_OK)


class ResetTransactionPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        # Generate and send OTP to the user's mobile number
        user = request.user
        send_otp(user.mobile)
        return Response({'otp': 'OTP sent'}, status=status.HTTP_200_OK)

    def put(self, request):
        # Validate OTP and reset the transaction password
        serializer = ResetTransactionPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            # Verify OTP
            if otp_storage.get(user.mobile) == int(otp):
                user.transaction_password = new_password
                user.save()
                return Response({'message': 'Transaction password reset successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

User = get_user_model()

class GetTransactionPasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        if hasattr(user, 'transaction_password'):
            return Response({'transaction_password': user.transaction_password}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Transaction password not set'}, status=status.HTTP_404_NOT_FOUND)

#exchange----


from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ExchangeSerializer

class ExchangeCreateView(generics.CreateAPIView):
    serializer_class = ExchangeSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        # Pass the request object to the serializer's context
        return {'request': self.request}

    def perform_create(self, serializer):
        # Ensure the user is saved with the exchange
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class ExchangeRetrieveView(generics.RetrieveAPIView):
    serializer_class = ExchangeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Return exchanges for the authenticated user
        return Exchange.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)
        exchange = get_object_or_404(queryset, id=lookup_value)
        return exchange

from rest_framework import generics
class ExchangeListView(generics.ListAPIView):
    queryset = Exchange.objects.all()  # Get all Exchange objects
    serializer_class = ExchangeSerializer


# withdrawal   

from decimal import Decimal
from django.db.models import Sum
class WithdrawalCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user  # Automatically get the authenticated user
        data = request.data.copy()  # Create a mutable copy of the request data

        # Get the network name from the request data
        network_name = data.get('network')
        network = get_object_or_404(Network, name=network_name)
        withdrawal_amount_str = data.get('amount')

        try:
            # Convert withdrawal amount to Decimal
            withdrawal_amount = Decimal(withdrawal_amount_str)
        except (ValueError, InvalidOperation):
            return Response(
                {'error': 'Invalid amount format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has deposited in the selected network
        deposits = Deposit.objects.filter(user=user, network=network, status='completed')
        total_deposited = deposits.aggregate(total=Sum('deposit_amount'))['total'] or Decimal('0.00')

        # Check if there is sufficient balance for the withdrawal
        if withdrawal_amount > total_deposited:
            return Response(
                {'error': 'Insufficient funds in the selected network.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a withdrawal already exists for this user
        existing_withdrawal = Withdrawal.objects.filter(user=user, network=network).first()

        if existing_withdrawal:
            # Ensure the wallet address is not changed
            if 'wallet_address' in data and data['wallet_address'] != existing_withdrawal.wallet_address:
                return Response(
                    {'error': 'Cannot change the wallet address after the first withdrawal.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Use the existing wallet address
            data['wallet_address'] = existing_withdrawal.wallet_address
        else:
            # Ensure a new wallet address is provided for the first withdrawal
            if 'wallet_address' not in data or not data['wallet_address']:
                return Response(
                    {'error': 'Wallet address is required for the first withdrawal.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Include the user in the data
        data['user'] = user.id
        data['network'] = network.id  # Store the network ID in the data
        data['status'] = 'pending'  # Set the status to pending by default

        serializer = WithdrawalSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            withdrawal = serializer.save()  # This should now properly save the user field
            response_data = serializer.data
            response_data['created_time'] = withdrawal.created_time  # Include created_time in the response
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class WithdrawalListView(generics.ListAPIView):
    serializer_class = WithdrawalListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Withdrawal.objects.filter(user=user).order_by('-created_time')




