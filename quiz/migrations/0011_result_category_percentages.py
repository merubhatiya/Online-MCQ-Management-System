# Generated by Django 5.0.7 on 2024-09-13 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_question_ctg_alter_question_option4'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='category_percentages',
            field=models.CharField(default='5', max_length=200),
        ),
    ]
