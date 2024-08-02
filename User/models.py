from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    # amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Changed to DecimalField
    initial_amount = models.IntegerField(default=0)


class UserTransaction(models.Model):
    user_id = models.ForeignKey(CustomUser, related_name="user_trans", on_delete=models.CASCADE, null=True)
    deposit_amount = models.FloatField(max_length=20)
    withdraw = models.FloatField(max_length=20)
    transaction_type = models.CharField(default="Blank", max_length=50)

