# Generated by Django 5.0.4 on 2025-05-29 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0007_alter_project_design_insight_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='combined_insight',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
