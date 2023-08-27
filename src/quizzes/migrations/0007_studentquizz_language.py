# Generated by Django 4.2.3 on 2023-08-19 19:33

from django.db import migrations, models
import src.common.constant


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0006_alter_questionlevel_choice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentquizz',
            name='language',
            field=models.CharField(choices=[('kz', 'KAZAKH'), ('ru', 'RUSSIAN')], db_index=True, default=src.common.constant.TestLang['KAZAKH'], max_length=64),
        ),
    ]