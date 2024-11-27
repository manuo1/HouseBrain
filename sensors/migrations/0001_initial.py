# Generated by Django 5.0 on 2024-11-20 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemperatureHumiditySensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', models.CharField(help_text='Adresse MAC du capteur', max_length=17, unique=True)),
                ('name', models.CharField(blank=True, help_text='Nom du capteur', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
