# Generated by Django 4.2.3 on 2023-08-20 10:38

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_coursetypelesson_main_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonPair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='lesson_images')),
                ('lesson_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_1', to='common.lesson')),
                ('lesson_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lesson_2', to='common.lesson')),
            ],
            options={
                'db_table': 'common"."lesson_pair',
            },
        ),
    ]
