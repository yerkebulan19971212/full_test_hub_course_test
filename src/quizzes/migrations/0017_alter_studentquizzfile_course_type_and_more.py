# Generated by Django 4.2.3 on 2023-10-25 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0020_alter_packet_name_en_alter_packet_name_kz_and_more"),
        ("quizzes", "0016_studentquizzfile_file_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="studentquizzfile",
            name="course_type",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="course_type_files",
                to="common.quizztype",
            ),
        ),
        migrations.AlterField(
            model_name="studentquizzfile",
            name="file",
            field=models.FileField(upload_to="student-quizz/file"),
        ),
        migrations.AlterField(
            model_name="studentquizzfile",
            name="icon",
            field=models.FileField(upload_to="student-quizz/icon"),
        ),
    ]