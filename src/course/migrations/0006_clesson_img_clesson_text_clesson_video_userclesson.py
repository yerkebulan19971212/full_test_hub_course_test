# Generated by Django 4.2.3 on 2024-03-16 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0005_rename_course_topic_coursetopic_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='clesson',
            name='img',
            field=models.FileField(null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='clesson',
            name='text',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='clesson',
            name='video',
            field=models.URLField(null=True),
        ),
        migrations.CreateModel(
            name='UserCLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('passed', models.BooleanField(default=False)),
                ('passed_time', models.DateTimeField(blank=True, null=True)),
                ('course_lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_c_lesson', to='course.clesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_c_lesson', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'course"."user_course_lesson',
            },
        ),
    ]
