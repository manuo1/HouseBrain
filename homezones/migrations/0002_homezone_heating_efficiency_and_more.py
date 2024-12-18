# Generated by Django 5.0 on 2024-12-07 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homezones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='homezone',
            name='heating_efficiency',
            field=models.PositiveIntegerField(default=100, help_text='< 100 % = piece longue à chauffer> 100 % = piece rapide à chauffer'),
        ),
        migrations.AddField(
            model_name='homezone',
            name='heating_efficiency_correction_mode',
            field=models.CharField(choices=[('manual', 'Manual'), ('auto', 'Automatic')], default='auto', help_text='heating_efficiency sera ajusté automatiquement sauf en mode manuel', max_length=10),
        ),
    ]
