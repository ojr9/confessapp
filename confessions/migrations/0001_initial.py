# Generated by Django 3.0.4 on 2020-03-24 21:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
                ('slug', models.SlugField(default='djangodbmodelsfieldscharfield')),
            ],
        ),
        migrations.CreateModel(
            name='Good',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('situation', models.TextField(default='')),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('intensity', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('likes', models.PositiveSmallIntegerField(default=0)),
                ('applauses', models.PositiveSmallIntegerField(default=0)),
                ('mehs', models.PositiveSmallIntegerField(default=0)),
                ('laughs', models.PositiveSmallIntegerField(default=0)),
                ('cries', models.PositiveSmallIntegerField(default=0)),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='confessions.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-registered'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('situation', models.TextField(default='')),
                ('registered', models.DateTimeField(auto_now_add=True)),
                ('intensity', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('likes', models.PositiveSmallIntegerField(default=0)),
                ('applauses', models.PositiveSmallIntegerField(default=0)),
                ('mehs', models.PositiveSmallIntegerField(default=0)),
                ('laughs', models.PositiveSmallIntegerField(default=0)),
                ('cries', models.PositiveSmallIntegerField(default=0)),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='confessions.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-registered'],
                'abstract': False,
            },
        ),
    ]