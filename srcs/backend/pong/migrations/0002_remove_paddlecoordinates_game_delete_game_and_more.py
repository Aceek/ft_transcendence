# Generated by Django 5.0.1 on 2024-02-19 02:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pong', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paddlecoordinates',
            name='game',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='PaddleCoordinates',
        ),
    ]
