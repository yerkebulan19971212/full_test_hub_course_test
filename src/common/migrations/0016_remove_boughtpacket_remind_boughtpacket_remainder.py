# Generated by Django 4.2.3 on 2023-08-27 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0015_boughtpacket_remind_boughtpacket_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='boughtpacket',
            name='remind',
        ),
        migrations.AddField(
            model_name='boughtpacket',
            name='remainder',
            field=models.IntegerField(default=0),
        ),
    ]