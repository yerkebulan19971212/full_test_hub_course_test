# Generated by Django 4.2.3 on 2023-08-28 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_boughtpacket_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='packet',
            name='name_en',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='packet',
            name='name_kz',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='packet',
            name='name_ru',
            field=models.CharField(default='', max_length=255),
        ),
    ]
