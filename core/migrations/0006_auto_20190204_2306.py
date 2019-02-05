# Generated by Django 2.1.2 on 2019-02-05 04:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190128_0000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='session',
            name='session_type',
            field=models.CharField(choices=[('R', 'Retro'), ('P', 'Poker')], max_length=10),
        ),
    ]
