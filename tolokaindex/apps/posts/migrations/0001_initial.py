# Generated by Django 3.0.3 on 2020-03-24 23:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('raw_posts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts',
                                                 to='posts.MediaItem')),
                ('raw_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='raw_posts.RawPost')),
                ('titles', models.ManyToManyField(to='posts.Title')),
                ('years', models.ManyToManyField(to='posts.Year')),
            ],
        ),
    ]
