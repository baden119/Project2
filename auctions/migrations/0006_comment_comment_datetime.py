# Generated by Django 3.0.8 on 2020-07-27 06:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_comment_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='comment_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date commented'),
            preserve_default=False,
        ),
    ]
