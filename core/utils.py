from django.contrib.auth.models import UserManager
from django.db.models import Q
import random
import string


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        return self.get(
            Q(**{self.model.USERNAME_FIELD: username}) |
            Q(**{self.model.EMAIL_FIELD: username})
        )


def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def generate_referral_code(user_id):
    # Generate a random 6-character alphanumeric string
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    # Combine user_id and random string to form a referral code
    return f"{user_id}{random_string}"