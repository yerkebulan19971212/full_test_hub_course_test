# Generated by Django 4.2.3 on 2024-11-17 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quizzes", "0029_studentanswer_lesson_studentscore_lesson"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
