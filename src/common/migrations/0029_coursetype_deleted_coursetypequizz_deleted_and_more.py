# Generated by Django 4.2.3 on 2024-03-09 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0028_packet_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetype',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coursetypequizz',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizztype',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
