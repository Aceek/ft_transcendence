# Generated by Django 5.0.1 on 2024-02-21 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_tournament_place_left'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matches',
            old_name='is_draw',
            new_name='is_in_game',
        ),
    ]
