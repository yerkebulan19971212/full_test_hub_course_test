# Generated by Django 4.2.3 on 2024-04-09 20:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0006_clesson_img_clesson_text_clesson_video_userclesson'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clesson',
            name='text',
        ),
        migrations.RemoveField(
            model_name='clesson',
            name='video',
        ),
        migrations.AddField(
            model_name='courselessontype',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='courselessontype',
            name='name_en',
            field=models.CharField(default=' ', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courselessontype',
            name='name_kz',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courselessontype',
            name='name_ru',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clesson',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='from_course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='course.course'),
        ),
        migrations.AlterField(
            model_name='courselessontype',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.CreateModel(
            name='CLessonContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name_kz', models.CharField(max_length=255)),
                ('name_ru', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('text', models.TextField(null=True)),
                ('video', models.URLField(null=True)),
                ('img', models.FileField(null=True, upload_to='')),
                ('file', models.FileField(null=True, upload_to='')),
                ('course_lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='c_lesson_content', to='course.clesson')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_lesson_content', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'course"."c_lesson_content',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name_kz', models.CharField(max_length=255)),
                ('name_ru', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('icon', models.FileField(blank=True, null=True, upload_to='')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='course.category')),
            ],
            options={
                'db_table': 'course"."category',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='course.category'),
        ),
    ]
