# Generated by Django 3.1.5 on 2021-03-17 22:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0002_title_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('season', models.PositiveIntegerField()),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasons',
                                           to='posts.post')),
            ],
        ),
        migrations.CreateModel(
            name='PostSeries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.PositiveIntegerField()),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='series',
                                             to='posts.postseason')),
            ],
        ),
    ]
