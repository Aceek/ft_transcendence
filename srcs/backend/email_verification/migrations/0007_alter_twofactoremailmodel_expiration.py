# Generated by Django 5.0.1 on 2024-01-22 07:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_verification', '0006_alter_twofactoremailmodel_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactoremailmodel',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2024, 1, 22, 8, 5, 11, 490800, tzinfo=datetime.timezone.utc)),
        ),
    ]
