# Generated by Django 5.0.7 on 2024-07-31 08:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0007_customuser_initial_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usertransaction',
            old_name='withdraw_amount',
            new_name='withdraw',
        ),
    ]
