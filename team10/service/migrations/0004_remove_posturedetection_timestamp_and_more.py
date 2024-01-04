# Generated by Django 4.2.7 on 2024-01-04 06:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0003_remove_posturedetection_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="posturedetection",
            name="timestamp",
        ),
        migrations.AddField(
            model_name="posturedetection",
            name="timehms",
            field=models.CharField(default="", max_length=8),
        ),
        migrations.AddField(
            model_name="posturedetection",
            name="timeymd",
            field=models.CharField(default="", max_length=10),
        ),
    ]