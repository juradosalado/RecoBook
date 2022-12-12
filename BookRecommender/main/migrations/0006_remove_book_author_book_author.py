# Generated by Django 4.1.2 on 2022-12-12 14:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_author"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="book",
            name="author",
        ),
        migrations.AddField(
            model_name="book",
            name="author",
            field=models.ManyToManyField(to="main.author"),
        ),
    ]
