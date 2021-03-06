# Generated by Django 3.0.4 on 2020-03-25 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('confessions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bad',
            name='private',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='good',
            name='private',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bad',
            name='situation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='good',
            name='situation',
            field=models.TextField(blank=True, null=True),
        ),
    ]
