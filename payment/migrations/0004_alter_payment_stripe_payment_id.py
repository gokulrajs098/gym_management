# Generated by Django 5.1 on 2024-10-04 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_alter_payment_stripe_payment_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='stripe_payment_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
