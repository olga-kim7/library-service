# Generated by Django 5.1 on 2024-08-19 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("borrowings_service", "0002_rename_book_id_borrowing_book_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="borrowing",
            options={"verbose_name_plural": "Borrowings"},
        ),
    ]
