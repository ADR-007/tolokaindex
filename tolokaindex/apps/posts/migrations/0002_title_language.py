# Generated by Django 3.1.5 on 2021-01-26 03:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='title',
            name='language',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
