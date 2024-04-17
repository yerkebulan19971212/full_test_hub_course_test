# Generated by Django 4.2.3 on 2024-04-16 19:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0009_remove_clesson_name_en_remove_clesson_name_kz_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clessoncontent',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='clessoncontent',
            name='name_kz',
        ),
        migrations.RemoveField(
            model_name='clessoncontent',
            name='name_ru',
        ),
        migrations.AddField(
            model_name='clesson',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clessoncontent',
            name='course_lesson_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_lesson_contents', to='course.courselessontype'),
        ),
        migrations.AlterField(
            model_name='clessoncontent',
            name='course_lesson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='c_lesson_contents', to='course.clesson'),
        ),
        migrations.AlterField(
            model_name='clessoncontent',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_lesson_contents', to=settings.AUTH_USER_MODEL),
        ),
    ]
