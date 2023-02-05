# Generated by Django 4.1.1 on 2023-02-05 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='color',
            field=models.CharField(choices=[('gray', 'gray'), ('yellow', 'yellow'), ('purple', 'purple'), ('orange', 'orange'), ('blue', 'blue'), ('green', 'green'), ('black', 'black'), ('maroon', 'maroon'), ('purple', 'purple'), ('fuchsia', 'fuchsia'), ('lime', 'lime'), ('navy', 'navy'), ('blueviolet', 'blueviolet'), ('cadetblue', 'cadetblue'), ('gold', 'gold'), ('indigo', 'indigo'), ('palevioletred', 'palevioletred')], default='gray', max_length=100),
        ),
    ]
