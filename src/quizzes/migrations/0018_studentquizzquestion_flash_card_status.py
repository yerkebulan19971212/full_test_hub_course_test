# Generated by Django 4.2.3 on 2023-11-01 15:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0017_alter_studentquizzfile_course_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentquizzquestion",
            name="flash_card_status",
            field=models.BooleanField(null=True),
        ),
    ]
