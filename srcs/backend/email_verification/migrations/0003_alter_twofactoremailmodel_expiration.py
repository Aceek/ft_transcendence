# Generated by Django 5.0.1 on 2024-02-19 02:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_verification', '0002_alter_twofactoremailmodel_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactoremailmodel',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 19, 2, 37, 58, 793477, tzinfo=datetime.timezone.utc)),
        ),
    ]