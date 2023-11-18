# Generated by Django 4.2.3 on 2023-11-15 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0023_ratingtest_boughtpacket_rating_test"),
        ("quizzes", "0019_studentquizz_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentquizz",
            name="bought_packet",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="student_quizzes",
                to="common.boughtpacket",
            ),
        ),
    ]
