# Generated by Django 3.0.4 on 2020-03-22 11:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200322_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(db_index=True, default=uuid.UUID('b309ecea-f9ac-4c41-b5c6-32b49eb9a239'), editable=False, primary_key=True, serialize=False),
        ),
    ]
