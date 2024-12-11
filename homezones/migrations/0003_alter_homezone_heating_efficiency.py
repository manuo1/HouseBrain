# Generated by Django 5.0 on 2024-12-10 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homezones', '0002_homezone_heating_efficiency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homezone',
            name='heating_efficiency',
            field=models.PositiveIntegerField(default=100, help_text='< 100 % = piece longue à chauffer  |  > 100 % = piece rapide à chauffer'),
        ),
    ]