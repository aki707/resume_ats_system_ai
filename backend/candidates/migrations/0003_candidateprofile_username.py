# Generated by Django 4.2.20 on 2025-03-27 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("candidates", "0002_remove_candidateprofile_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="username",
            field=models.CharField(
                default="default_username", max_length=150, unique=True
            ),
        ),
    ]
