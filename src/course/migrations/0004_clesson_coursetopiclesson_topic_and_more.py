# Generated by Django 4.2.3 on 2024-03-12 19:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0003_alter_coursetopicm2m_course_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CLesson',
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
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(null=True)),
                ('course_lesson_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='c_lessons', to='course.courselessontype')),
                ('from_course_lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.clesson')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='c_lessons', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'course"."c_lessons',
            },
        ),
        migrations.CreateModel(
            name='CourseTopicLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('course_lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic_lessons', to='course.clesson')),
            ],
            options={
                'db_table': 'course"."course_topic_lesson',
            },
        ),
        migrations.CreateModel(
            name='Topic',
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
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('description', models.TextField(null=True)),
                ('from_course_topic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.topic')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topics', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'course"."topic',
            },
        ),
        migrations.RemoveField(
            model_name='coursetopiclessonm2m',
            name='course_lesson',
        ),
        migrations.RemoveField(
            model_name='coursetopiclessonm2m',
            name='course_topic',
        ),
        migrations.RemoveField(
            model_name='coursetopiclessonm2m',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='coursetopicm2m',
            name='course',
        ),
        migrations.RemoveField(
            model_name='coursetopicm2m',
            name='course_topic',
        ),
        migrations.RemoveField(
            model_name='coursetopicm2m',
            name='from_course_topic',
        ),
        migrations.RemoveField(
            model_name='coursetopicm2m',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='coursetopic',
            name='description',
        ),
        migrations.RemoveField(
            model_name='coursetopic',
            name='name_code',
        ),
        migrations.RemoveField(
            model_name='coursetopic',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='coursetopic',
            name='name_kz',
        ),
        migrations.RemoveField(
            model_name='coursetopic',
            name='name_ru',
        ),
        migrations.AddField(
            model_name='coursetopic',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic', to='course.course'),
        ),
        migrations.AddField(
            model_name='coursetopic',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coursetopic',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='CourseLesson',
        ),
        migrations.DeleteModel(
            name='CourseTopicLessonM2M',
        ),
        migrations.DeleteModel(
            name='CourseTopicM2M',
        ),
        migrations.AddField(
            model_name='coursetopiclesson',
            name='course_topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic_lessons', to='course.coursetopic'),
        ),
        migrations.AddField(
            model_name='coursetopiclesson',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic_lessons', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coursetopic',
            name='course_topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_topic', to='course.topic'),
        ),
    ]