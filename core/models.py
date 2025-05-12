from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# User model with user_type to differentiate roles
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('agent', 'Agent'),
        ('consumer', 'Consumer'),
        ('merchant', 'Merchant'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

# AgentProfile model
class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=255)

# ConsumerProfile model
class ConsumerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='consumer_profile')
    address = models.TextField()
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add balance field

# MerchantProfile model
class MerchantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant_profile')
    store_name = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add balance field

# Transaction model
class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('cash_in', 'Cash In'),
        ('cash_out', 'Cash Out'),
        ('bill_payment', 'Bill Payment'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')
    reference_id = models.CharField(max_length=100, unique=True)

# Bill model
class Bill(models.Model):
    bill_type = models.CharField(max_length=50)
    account_number = models.CharField(max_length=50)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

# BillPayment model
class BillPayment(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='bill_payment')
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='bill_payments')
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bill_payments')

# Product model
class Product(models.Model):
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Service model
class Service(models.Model):
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    subscription_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Subscription model
class Subscription(models.Model):
    consumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='subscriptions')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'consumer':
            ConsumerProfile.objects.create(user=instance)
        elif instance.user_type == 'merchant':
            MerchantProfile.objects.create(user=instance)
        elif instance.user_type == 'agent':
            AgentProfile.objects.create(user=instance)
