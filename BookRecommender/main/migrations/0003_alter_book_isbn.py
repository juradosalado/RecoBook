# Generated by Django 4.1.2 on 2022-12-09 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0002_alter_book_publish_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.TextField(primary_key=True, serialize=False),
        ),
    ]
