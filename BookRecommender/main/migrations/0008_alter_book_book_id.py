# Generated by Django 4.1.2 on 2022-12-12 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_rename_isbn_book_book_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="book_id",
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
