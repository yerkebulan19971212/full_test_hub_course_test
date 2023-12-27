# Generated by Django 4.2.3 on 2023-12-27 11:37

from django.db import migrations, models
import src.common.constant


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0021_question_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[("DEFAULT", "DEFAULT"), ("SELECT", "SELECT")],
                default=src.common.constant.QuestionType["DEFAULT"],
                max_length=11,
            ),
        ),
    ]
