# Generated by Django 5.0.7 on 2024-08-22 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet_app', '0011_withdrawal_wallet_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawal',
            name='wallet_address',
            field=models.CharField(max_length=255),
        ),
    ]
