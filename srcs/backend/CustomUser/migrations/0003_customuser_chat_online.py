# Generated by Django 5.0.1 on 2024-02-26 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CustomUser', '0002_customuser_blocked_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='chat_online',
            field=models.BooleanField(blank=True, default=False, editable=False),
        ),
    ]
