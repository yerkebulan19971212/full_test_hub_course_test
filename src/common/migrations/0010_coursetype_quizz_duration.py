# Generated by Django 4.2.3 on 2023-08-24 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_remove_lesson_course_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetype',
            name='quizz_duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
