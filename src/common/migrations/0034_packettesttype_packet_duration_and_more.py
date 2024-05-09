# Generated by Django 4.2.3 on 2024-05-06 09:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0033_blog_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PacketTestType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('name_kz', models.CharField(max_length=255)),
                ('name_ru', models.CharField(max_length=255)),
                ('name_en', models.CharField(max_length=255)),
                ('name_code', models.CharField(blank=True, max_length=255, null=True, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='packet',
            name='duration',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AddField(
            model_name='packet',
            name='question_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='packet',
            name='subject_quantity',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='packet',
            name='packet_test_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='packets', to='common.packettesttype'),
        ),
    ]