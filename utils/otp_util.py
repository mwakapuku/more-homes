import random
from datetime import timedelta

import nextsms
from django.utils import timezone

from utils.logger import AppLogger

logger = AppLogger(__name__)


class OtpUtil:
    def __init__(self, user, reset_otp: bool = False):
        self.user = user
        self.reset_otp = reset_otp
        self.logger = AppLogger(__name__)

    def generate_and_send_otp(self):
        if not self.user.phone:
            return False, "User does not have phone number"

        otp_code = str(random.randint(1000, 9999))
        self.send_otp(otp_code)

        print(f"sending otp {otp_code}")

        self.user.otp = otp_code
        self.user.otp_expiry = timezone.now() + timedelta(minutes=2)
        self.user.reset_otp = self.reset_otp
        self.user.max_otp_try = 3
        self.user.otp_max_out = None
        self.user.save()

        print(f"saved otp {self.user.otp}")

        return True

    def send_otp(self, otp_code):
        self.logger.info(f"DEBUG: Sending OTP {otp_code} to {self.user.phone} for user {self.user.username}")
        self.send_sms_to_user(self.user.phone, f"Your OTP is: {otp_code}")
        return True

    def send_sms_to_user(self, phone: str, msg: str) -> dict:
        """Send SMS to user using NextSMS gateway.
        Args:
            phone: Recipient's number (format '2557xxxxxxx')
            msg: Message content
        Returns:
            {'msg': 'success', 'results': sms_response}
        """
        sender = nextsms('FadhilaMbura', 'Faramas@2025')
        phone = f"{phone[1:]}"  # Remove leading '2'
        responses = sender.sendsms(
            message=msg,
            recipients=[phone],
            sender_id="FARAMAS Co"
        )
        return {'msg': 'success', 'results': responses}

    # check if the otp expired
    def verify_otp_expiry(self):
        if self.user.otp_expiry and timezone.now() > self.user.otp_expiry:
            self.logger.error(f"❌Error:OTP expiry. for {self.user.username}")
            return False
        return True

    # Check max OTP tries
    def verify_otp_max_time(self):
        if self.user.otp_max_out and timezone.now() < self.user.otp_max_out:
            self.logger.error(f"❌Error: Too many OTP attempts. Try again later. for {self.user.username}")
            return False

        return True

    # check max retries
    def check_max_limit(self):
        self.logger.info(f"🔥Debug:increase max retries")
        if int(self.user.max_otp_try) <= 0:
            self.logger.info(f"🔥Debug: Check timezone")
            self.user.otp_max_out = timezone.now() + timedelta(minutes=10)
            self.user.max_otp_try = 3
            self.user.save()
            return True
        return False

    # verify user used during verification of user
    def verify_user(self):
        try:
            self.logger.info(f"🔥DEBUG: Verifying user {self.user.username}")
            self.user.verified = True
            self.user.save()
            msg = f"Congratulations, account with username {self.user.username} verified successfully"
            self.send_sms_to_user(self.user.phone, msg)
            return True
        except Exception as e:
            self.logger.error("❌Error: Error verifying user: " + str(e))
            return False

    # verify if the otp validity
    def verify_otp(self, otp_code):
        self.logger.error(f"🔥Debug:Verifying otp {otp_code}")
        if not self.user.otp == otp_code:
            self.logger.error(f"❌Error: Invalid otp {otp_code} user otp is {self.user.otp}")
            return False

        self.clear_user_otp()
        self.logger.info(f"✅Debug:otp are valid {otp_code}")
        return True

    # decrease max retry
    def decrease_max_retries(self):
        self.logger.info(f"🔥Debug:increase max retries")
        self.user.max_otp_try = str(int(self.user.max_otp_try) - 1)
        self.user.save()

        return f"Incorrect OTP. {self.user.max_otp_try} attempts remaining."

    # clear user otp
    def clear_user_otp(self):
        try:
            self.logger.info(f"🔥DEBUG: Clear user otp user {self.user.username}")
            self.user.otp = None
            self.user.otp_expiry = None
            self.user.max_otp_try = 3
            self.user.otp_max_out = None
            self.user.save()
            return True

        except Exception as e:
            self.logger.error("❌Error: Error while clear user otp: " + str(e))
            return False
