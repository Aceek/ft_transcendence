# Generated by Django 5.0.1 on 2024-03-22 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0011_rename_localmatch_localmatches'),
    ]

    operations = [
        migrations.RenameField(
            model_name='localmatches',
            old_name='player1',
            new_name='user1',
        ),
        migrations.RenameField(
            model_name='localmatches',
            old_name='player2',
            new_name='user2',
        ),
    ]
