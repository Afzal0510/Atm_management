# Generated by Django 5.0.7 on 2024-07-31 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0006_usertransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='initial_amount',
            field=models.IntegerField(default=0),
        ),
    ]
