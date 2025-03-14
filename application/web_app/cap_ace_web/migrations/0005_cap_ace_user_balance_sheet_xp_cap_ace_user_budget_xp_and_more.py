# Generated by Django 5.1.1 on 2025-02-16 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_ace_web', '0004_alter_multiplechoice_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='cap_ace_user',
            name='balance_sheet_xp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cap_ace_user',
            name='budget_xp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cap_ace_user',
            name='credit_xp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cap_ace_user',
            name='investing_xp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cap_ace_user',
            name='savings_xp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cap_ace_user',
            name='taxes_xp',
            field=models.IntegerField(default=0),
        ),
    ]
