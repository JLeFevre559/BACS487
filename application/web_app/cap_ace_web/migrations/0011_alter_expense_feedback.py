# Generated by Django 5.1.1 on 2025-03-30 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_ace_web', '0010_budgetsimulation_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='feedback',
            field=models.TextField(help_text="Provide feedback on why this expense is or isn't essential"),
        ),
    ]
