# Generated by Django 5.1.7 on 2025-03-17 22:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='joined_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
