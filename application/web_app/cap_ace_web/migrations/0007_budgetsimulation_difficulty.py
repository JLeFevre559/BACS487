# Generated by Django 5.1.1 on 2025-03-04 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_ace_web', '0006_budgetsimulation_expense'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetsimulation',
            name='difficulty',
            field=models.CharField(choices=[('B', 'Beginner'), ('I', 'Intermediate'), ('A', 'Advanced')], default='B', max_length=1),
        ),
    ]
