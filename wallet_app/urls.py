

from django.urls import path
from wallet_app.views import *


urlpatterns = [
    path('platform_price/',Platform_pricelist.as_view(),name='platform_pricelist'), 
    path('announcement/',announcementlist.as_view(),name='announcementlist'), 
    path('exchange/',Exchange_pricelist.as_view(),name='exchangliste'),
            
    path('auth/login_register/', LoginRegisterAPIView.as_view(), name='login_register'),
    path('auth/verify_otp/', VerifyOtpAPIView.as_view(), name='verify_otp'),
    path('auth/resend_otp/', ResendOtpAPIView.as_view(), name='resend_otp'),
    path('auth/otp_autofill/', OTPAutofillView.as_view(), name='otp_autofill'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),

    path('bank-details/', BankDetailsManageView.as_view(), name='bank-details-create'),
    path('bank-details/<int:id>/update/', BankDetailsUpdateView.as_view(), name='bank-details-update'),
    path('bank-details/<int:id>/delete/', BankDetailsDeleteView.as_view(), name='bank-details-delete'),

    path('deposits/choose-network/', ChooseNetworkAPIView.as_view(), name='choose-network'),
    path('deposits/get-deposit-address/', GetDepositAddressAPIView.as_view(), name='get-deposit-address'),
    path('deposits/enter-amount/', EnterDepositAmountView.as_view(), name='enter-deposit-amount'),
    path('deposits/available-balance/', AvailableBalanceAPIView.as_view(), name='available-balance'),
    path('deposits/history/', DepositHistoryAPIView.as_view(), name='deposit-history'),

    path('set-transaction-password/', SetTransactionPasswordAPIView.as_view(), name='set_transaction_password'),
    path('reset-transaction-password/', ResetTransactionPasswordAPIView.as_view(), name='reset_transaction_password'),
    path('get-transaction-password/', GetTransactionPasswordAPIView.as_view(), name='get_transaction_password'),

    path('exchange/create/', ExchangeCreateView.as_view(), name='exchange-create'),
    path('exchanges/', ExchangeListView.as_view(), name='exchange-list'),
    path('exchange/<int:id>/', ExchangeRetrieveView.as_view(), name='exchange-detail'),


    

    # path('withdrawals/', WithdrawalListView.as_view(), name='withdrawal-list'),
    # path('withdrawals/<int:pk>/', WithdrawalDetailView.as_view(), name='withdrawal-detail'),
    path('withdrawals/', WithdrawalListView.as_view(), name='withdrawal-list'),
    path('withdrawals/create/', WithdrawalCreateView.as_view(), name='withdrawal-create'),
]
