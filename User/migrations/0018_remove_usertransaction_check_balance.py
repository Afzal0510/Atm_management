# Generated by Django 5.0.7 on 2024-08-05 11:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0017_customuser_is_login_alter_customuser_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertransaction',
            name='check_balance',
        ),
    ]
