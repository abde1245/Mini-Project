# Generated by Django 5.2.1 on 2025-05-13 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_submissions', '0003_alter_submission_grading_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='grading_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
