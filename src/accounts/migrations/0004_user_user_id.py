# Generated by Django 4.2.3 on 2023-08-29 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='user_id',
            field=models.IntegerField(null=True, unique=True),
        ),
    ]
