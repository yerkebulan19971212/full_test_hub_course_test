# Generated by Django 4.2.3 on 2023-11-08 09:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0021_school"),
    ]

    operations = [
        migrations.AddField(
            model_name="packet",
            name="name_code",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
