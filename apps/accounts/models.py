import uuid
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom user model for NexMedia with UUID primary key,
    dual credit wallets (Standard & Premium), and profile metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    standard_credits = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0.0000'))
    premium_credits = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0.0000'))
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    avatar_url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'nexmedia_users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username or self.email
