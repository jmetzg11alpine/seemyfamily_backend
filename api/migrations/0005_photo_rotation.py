# Generated by Django 5.1.2 on 2024-11-04 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_location_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='rotation',
            field=models.ImageField(default=0, upload_to=''),
        ),
    ]
