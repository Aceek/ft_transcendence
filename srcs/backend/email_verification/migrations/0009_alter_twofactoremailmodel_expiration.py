# Generated by Django 5.0.1 on 2024-02-24 11:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_verification', '0008_alter_twofactoremailmodel_expiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twofactoremailmodel',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 24, 12, 9, 0, 830059, tzinfo=datetime.timezone.utc)),
        ),
    ]
