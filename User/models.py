from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    initial_amount = models.IntegerField(default=0)
    is_login = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    open_balance = models.IntegerField(default=0)


class UserTransaction(models.Model):
    user_id = models.ForeignKey(CustomUser, related_name="user_trans", on_delete=models.CASCADE, null=True)
    deposit_amount = models.FloatField(max_length=20)
    withdraw = models.FloatField(max_length=20)
    transaction_type = models.CharField(default="Blank", max_length=50)
