# Generated by Django 3.0.4 on 2020-03-22 13:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200322_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(db_index=True, default=uuid.UUID('c3e91f2c-3510-4e75-988e-a39f2cb1ca3c'), editable=False, primary_key=True, serialize=False),
        ),
    ]
