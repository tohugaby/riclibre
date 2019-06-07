# Generated by Django 2.2.1 on 2019-06-06 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0004_auto_20190606_1637'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='achievement',
            constraint=models.UniqueConstraint(fields=('user', 'badge'), name='user_badge_unique'),
        ),
    ]