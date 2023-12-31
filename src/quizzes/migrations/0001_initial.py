# Generated by Django 4.2.3 on 2023-08-19 07:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import src.common.constant
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0007_coursetypelesson_main_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('point', models.PositiveSmallIntegerField(db_index=True, default=0)),
                ('choice', models.PositiveSmallIntegerField(choices=[(0, 'CHOICE')], db_index=True, default=src.common.constant.ChoiceType['CHOICE'])),
            ],
            options={
                'db_table': 'quizz"."question_level',
            },
        ),
        migrations.CreateModel(
            name='Variant',
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
                ('language', models.CharField(choices=[('kz', 'KAZAKH'), ('ru', 'RUSSIAN')], db_index=True, default=src.common.constant.TestLang['KAZAKH'], max_length=64)),
                ('variant_title', models.IntegerField()),
                ('course_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='common.coursetype')),
            ],
            options={
                'db_table': 'quizz"."variant',
            },
        ),
        migrations.CreateModel(
            name='StudentQuizz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('NOT_PASSED', 'NOT_PASSED'), ('CONTINUE', 'CONTINUE'), ('PASSED', 'PASSED'), ('EXPIRED', 'EXPIRED')], default=src.common.constant.QuizzStatus['NOT_PASSED'], max_length=12)),
                ('quizz_type', models.CharField(choices=[('BY_LESSON', 'BY_LESSON'), ('FULL_TEST_ENT', 'FULL_TEST_ENT'), ('INFINITY_QUIZ', 'INFINITY_QUIZ')], max_length=128)),
                ('quizz_start_time', models.DateTimeField(blank=True, null=True)),
                ('quizz_end_time', models.DateTimeField(blank=True, null=True)),
                ('course_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_quizzes', to='common.coursetype')),
                ('lesson', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_quizzes', to='common.lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_quizzes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'quizz"."student_test',
            },
        ),
        migrations.CreateModel(
            name='LessonQuestionLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('number_of_questions', models.IntegerField(db_index=True, default=0)),
                ('question_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_question_level', to='quizzes.questionlevel')),
                ('test_type_lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_question_level', to='common.coursetypelesson')),
            ],
            options={
                'db_table': 'quizz"."lesson_question_level',
                'unique_together': {('test_type_lesson', 'question_level')},
            },
        ),
    ]
