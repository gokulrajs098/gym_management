# Generated by Django 5.1 on 2024-09-24 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_mentors', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mentors',
            name='is_login',
            field=models.BooleanField(default=False),
        ),
    ]
