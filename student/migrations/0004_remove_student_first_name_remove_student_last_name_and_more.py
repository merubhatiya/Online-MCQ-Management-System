# Generated by Django 5.0.7 on 2024-09-09 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_remove_student_std_student_first_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='student',
            name='password',
        ),
        migrations.RemoveField(
            model_name='student',
            name='username',
        ),
        migrations.AlterField(
            model_name='student',
            name='address',
            field=models.CharField(max_length=40),
        ),
    ]
