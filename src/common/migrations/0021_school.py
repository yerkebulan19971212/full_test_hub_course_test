# Generated by Django 4.2.3 on 2023-11-01 16:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0020_alter_packet_name_en_alter_packet_name_kz_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="School",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("order", models.IntegerField(db_index=True, default=1)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("name_kz", models.CharField(max_length=255)),
                ("name_ru", models.CharField(max_length=255)),
                ("name_en", models.CharField(max_length=255)),
                (
                    "name_code",
                    models.CharField(
                        blank=True, max_length=255, null=True, unique=True
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schools",
                        to="common.city",
                    ),
                ),
            ],
            options={
                "db_table": 'common"."school',
            },
        ),
    ]
