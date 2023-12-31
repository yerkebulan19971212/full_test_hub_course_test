# Generated by Django 4.2.3 on 2023-08-19 07:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quizzes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnswerSign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
            options={
                'db_table': 'quizz"."answer_sign',
            },
        ),
        migrations.CreateModel(
            name='CommonQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
            ],
            options={
                'db_table': 'quizz"."common_question',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(db_index=True, default=1)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('question', models.TextField(null=True)),
                ('math', models.BooleanField(default=False)),
                ('common_question', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='quizzes.commonquestion')),
                ('lesson_question_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quizzes.lessonquestionlevel')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.variant')),
            ],
            options={
                'db_table': 'quizz"."question',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('answer', models.TextField()),
                ('correct', models.BooleanField(default=False)),
                ('math', models.BooleanField(default=False)),
                ('answer_sign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizzes.answersign')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='quizzes.question')),
            ],
            options={
                'db_table': 'quizz"."answer',
            },
        ),
    ]
