# Generated by Django 4.2.3 on 2023-08-26 18:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_packet'),
        ('quizzes', '0012_studentquizz_quizz_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentquizz',
            name='packet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_quizzes', to='common.packet'),
        ),
    ]