# Generated by Django 3.0.4 on 2020-03-22 11:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.UUIDField(db_index=True, default=uuid.UUID('b87de98d-4d58-412f-ab65-c4600060966e'), editable=False, primary_key=True, serialize=False),
        ),
    ]
