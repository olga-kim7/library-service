# Generated by Django 5.1 on 2024-08-22 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("borrowings_service", "0003_alter_borrowing_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]