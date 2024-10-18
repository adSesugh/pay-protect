from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils import CustomUserManager


class User(AbstractUser):
    terms = models.BooleanField(default=True)
    referral_code = models.CharField(max_length=100, blank=True)
    referral = models.CharField(max_length=100, blank=True)
    notify_on_request = models.BooleanField(default=False)
    notify_on_payment = models.BooleanField(default=False)
    notify_on_milestone = models.BooleanField(default=False)
    photo_url = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()


class Bank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'banks'


class PayoutAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    account_number = models.PositiveIntegerField(unique=True)
    account_name = models.CharField(max_length=100)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payout_accounts'

    def __str__(self):
        return f'{self.account_name} - {self.account_number}'


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='receiver')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/%Y/%m/%d/')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name


class ContractQuestion(models.Model):
    question = models.TextField()
    additions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class Agreement(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    question = models.ForeignKey(ContractQuestion, on_delete=models.CASCADE)
    answer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('receiver', 'product', 'question'),)

    def __str__(self):
        return self.question.question


class DisputeReason(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reason


class Dispute(models.Model):
    DISPUTE_CHOICES = [
        ('PENDING', 'PENDING'),
        ('TREATED', 'TREATED'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reason = models.ForeignKey(DisputeReason, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(choices=DISPUTE_CHOICES, default='PENDING', max_length=50)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description


class DisputeImage(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.dispute.description


class ProtectionFee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_percent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FAQs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
