# Generated by Django 4.2.7 on 2023-12-29 02:30

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_usersession"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="address",
        ),
    ]