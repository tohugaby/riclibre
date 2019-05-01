# Generated by Django 2.2.1 on 2019-05-01 17:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('id_card_checker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='idcard',
            name='creation',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date de création'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='idcard',
            name='update',
            field=models.DateTimeField(auto_now=True, verbose_name='Date de mise à jour'),
        ),
    ]
