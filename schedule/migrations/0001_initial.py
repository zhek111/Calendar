import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256, verbose_name='subject')),
            ],
        ),
        migrations.CreateModel(
            name='WorkDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField(default=True, help_text='Writable', verbose_name='availability')),
                ('date', models.DateField(help_text='Date', verbose_name='date')),
                ('start', models.TimeField(default=datetime.time(9, 0), help_text='Set the beginning of the work day', verbose_name='start')),
                ('finish', models.TimeField(default=datetime.time(18, 0), help_text='Set the end of the working day', verbose_name='end')),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration_lessons', models.IntegerField(verbose_name='duration')),
                ('start', models.TimeField(help_text='lesson start time', verbose_name='start')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('change_at', models.DateTimeField(auto_now=True)),
                ('comment', models.CharField(help_text='comment', max_length=512, verbose_name='comment')),
                ('day', models.ForeignKey(help_text='Day', on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='schedule.workday', verbose_name='day')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='schedule.subject')),
            ],
        ),
    ]
