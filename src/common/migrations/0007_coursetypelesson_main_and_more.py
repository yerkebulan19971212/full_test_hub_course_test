# Generated by Django 4.2.3 on 2023-08-19 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0006_rename_uuid_field_city_uuid_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetypelesson',
            name='main',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coursetypelesson',
            name='questions_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterUniqueTogether(
            name='coursetypelesson',
            unique_together={('course_type', 'lesson')},
        ),
        migrations.RemoveField(
            model_name='coursetypelesson',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='coursetypelesson',
            name='name_code',
        ),
        migrations.RemoveField(
            model_name='coursetypelesson',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='coursetypelesson',
            name='name_kz',
        ),
        migrations.RemoveField(
            model_name='coursetypelesson',
            name='name_ru',
        ),
    ]
