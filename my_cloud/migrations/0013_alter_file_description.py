# Generated by Django 5.0.4 on 2024-04-28 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_cloud', '0012_alter_file_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
