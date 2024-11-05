# Generated by Django 5.0 on 2024-11-06 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Radiator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Nom')),
                ('power', models.PositiveIntegerField(verbose_name='Puissance (W)')),
                ('control_pin', models.PositiveSmallIntegerField(choices=[(0, 'Pin 0'), (1, 'Pin 1'), (2, 'Pin 2'), (3, 'Pin 3'), (4, 'Pin 4'), (5, 'Pin 5'), (6, 'Pin 6'), (7, 'Pin 7'), (8, 'Pin 8'), (9, 'Pin 9'), (10, 'Pin 10'), (11, 'Pin 11'), (12, 'Pin 12'), (13, 'Pin 13'), (14, 'Pin 14'), (15, 'Pin 15')], unique=True, verbose_name='Pin MCP23017')),
                ('priority', models.PositiveSmallIntegerField(help_text='Plus la valeur est basse, plus la priorité est élevée pour rester allumé.', verbose_name='Priorité de délestage')),
                ('is_on', models.BooleanField(default=False, verbose_name='Allumé')),
            ],
        ),
    ]
