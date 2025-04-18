# Generated by Django 5.1.1 on 2025-03-30 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_ace_web', '0008_fillintheblank'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlashCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=100)),
                ('answer', models.BooleanField(default=False)),
                ('feedback', models.TextField()),
                ('category', models.CharField(choices=[('BUD', 'Budgeting'), ('INV', 'Investing'), ('SAV', 'Savings'), ('BAL', 'Balance Sheet'), ('CRD', 'Credit'), ('TAX', 'Taxes')], max_length=3, null=True)),
                ('difficulty', models.CharField(choices=[('B', 'Beginner'), ('I', 'Intermediate'), ('A', 'Advanced')], default='B', max_length=1)),
            ],
        ),
        migrations.AddField(
            model_name='fillintheblank',
            name='category',
            field=models.CharField(choices=[('BUD', 'Budgeting'), ('INV', 'Investing'), ('SAV', 'Savings'), ('BAL', 'Balance Sheet'), ('CRD', 'Credit'), ('TAX', 'Taxes')], max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='fillintheblank',
            name='feedback',
            field=models.TextField(default=''),
        ),
    ]
