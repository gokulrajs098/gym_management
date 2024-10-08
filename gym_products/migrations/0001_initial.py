# Generated by Django 5.1 on 2024-09-06 17:10

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gym_details', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GymProducts',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=50)),
                ('desc', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to='pics')),
                ('reviews', models.CharField(max_length=100)),
                ('stock', models.IntegerField()),
                ('stripe_product_id', models.CharField(blank=True, max_length=50, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=50, null=True)),
                ('Gym', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gym_details.gymdetails')),
            ],
        ),
    ]
