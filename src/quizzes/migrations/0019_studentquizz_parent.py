# Generated by Django 4.2.3 on 2023-11-01 16:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0018_studentquizzquestion_flash_card_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentquizz",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="quizzes.studentquizz",
            ),
        ),
    ]