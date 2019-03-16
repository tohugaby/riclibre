# Generated by Django 2.1.7 on 2019-03-12 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referendum', '0002_auto_20190307_1810'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referendum',
            name='event_end',
        ),
        migrations.AddField(
            model_name='referendum',
            name='duration',
            field=models.IntegerField(choices=[(86399, '24h')], default=86399, verbose_name='Durée des votes'),
        ),
    ]
