# Generated by Django 4.2.3 on 2023-09-01 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_boughtpacket_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='choose_icon',
            field=models.FileField(blank=True, null=True, upload_to='lesson/choose'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to='lesson'),
        ),
    ]
