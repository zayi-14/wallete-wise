# utils.py
from twilio.rest import Client
from django.conf import settings

def send_verification_code(phone, code):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Your verification code is {code}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone
    )
    return message.sid
