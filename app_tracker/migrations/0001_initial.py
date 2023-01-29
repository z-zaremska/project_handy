# Generated by Django 4.1.1 on 2023-01-29 12:32

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='activity name', max_length=200)),
                ('color', models.CharField(choices=[('gray', 'gray'), ('yellow', 'yellow'), ('purple', 'purple'), ('orange', 'orange'), ('blue', 'blue'), ('green', 'green'), ('black', 'black')], default='gray', max_length=100)),
            ],
            options={
                'verbose_name_plural': 'activities',
            },
        ),
        migrations.CreateModel(
            name='TimeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('start_time', models.TimeField(default=django.utils.timezone.now)),
                ('log_time', models.DurationField(default=datetime.timedelta(seconds=1800))),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_logs', to='app_tracker.activity')),
            ],
            options={
                'verbose_name_plural': 'timelogs',
                'ordering': ['-date', '-start_time'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='category name', max_length=30, unique=True)),
                ('description', models.CharField(default='category description', max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.AddField(
            model_name='activity',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='all_activities', to='app_tracker.category'),
        ),
    ]