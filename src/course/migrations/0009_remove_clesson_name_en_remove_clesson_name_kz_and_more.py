# Generated by Django 4.2.3 on 2024-04-10 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0008_alter_category_managers_remove_course_name_en_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clesson',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='clesson',
            name='name_kz',
        ),
        migrations.RemoveField(
            model_name='clesson',
            name='name_ru',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='name_kz',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='name_ru',
        ),
        migrations.AddField(
            model_name='clesson',
            name='title',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='topic',
            name='title',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
