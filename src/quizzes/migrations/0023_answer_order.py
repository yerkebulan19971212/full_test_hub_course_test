# Generated by Django 4.2.3 on 2024-01-05 14:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0022_question_question_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="answer",
            name="order",
            field=models.IntegerField(db_index=True, default=1),
        ),
    ]
