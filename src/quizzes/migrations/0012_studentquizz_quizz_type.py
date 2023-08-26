# Generated by Django 4.2.3 on 2023-08-26 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_alter_quizztype_options_alter_quizztype_icon'),
        ('quizzes', '0011_remove_studentquizz_quizz_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentquizz',
            name='quizz_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_quizzes', to='common.coursetypequizz'),
        ),
    ]
