# Generated by Django 5.0.4 on 2025-05-29 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0010_project_latitude_project_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='material',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
