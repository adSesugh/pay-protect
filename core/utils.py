import json
import random
import logging
import requests
from django.core.mail import EmailMessage
from django.conf import settings
from core.models import User, OneTimePassword
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    """Generates a secure one-time password (OTP) of given length."""
    return ''.join(str(random.SystemRandom().randint(0, 9)) for _ in range(length))


def send_code_to_user(email):
    """Sends a one-time passcode to the user's email for verification."""
    subject = 'One-time passcode for Email verification'
    otp_code = generate_otp(length=6)

    current_site = 'PayProtect - Protecting buyer and sellers value'
    email_body = f'Hi,\n\nThanks for signing up on {current_site}. Please verify your email with the one-time passcode: {otp_code}'
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.create(verification_type=email, code=otp_code)

    send_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])

    try:
        send_email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Failed to send email to {email}. Error: {e}")  # Logging
        return False


def send_sms_otp(recipient):
    """Send OTP via SMS using Kudisms."""
    otp = generate_otp(length=6)
    message = f"Your OTP is {otp}"

    recipient = recipient.replace('+', '')

    SMS_BASE_URL = f'https://my.kudisms.net/api/sms?token={settings.KUDISMS_API_KEY}&senderID={settings.KUDISMS_SENDER_ID}'

    formatted_url = f"{SMS_BASE_URL}&recipients={recipient}&message={message}&gateway=2"

    try:
        response = requests.get(formatted_url)
        print(response.json())
        response.raise_for_status()  # Check for HTTP errors
        logger.info(f"Sent OTP to recipient: {recipient}")
        return otp
    except requests.RequestException as e:
        logger.error(f"Failed to send OTP to recipient: {recipient}. Error: {e}")
        return None


def validate_otp(verification_type, otp_code):
    """Validates the OTP for a given verification type."""

    try:
        otp_record = OneTimePassword.objects.get(verification_type=verification_type, code=otp_code)
        if otp_record.is_valid():
            logger.info(f'OTP for user {verification_type} is valid.')
            return True
        else:
            logger.warning(f'OTP for user {verification_type} has expired.')
            return False
    except OneTimePassword.DoesNotExist:
        logger.warning(f'Invalid OTP for user {verification_type}.')
        return False


def create_otp(verification_type, otp_code):
    try:
        with transaction.atomic():
            logger.debug(f"Creating new OTP for user: {verification_type}")
            OneTimePassword.objects.create(verification_type=verification_type, code=otp_code)
            logger.debug(f"Created new OTP for user: {verification_type}")
        return True
    except Exception as e:
        logger.error(f"Failed to create OTP for user: {verification_type}, error: {str(e)}")
        return False
