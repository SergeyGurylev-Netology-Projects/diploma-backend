# Generated by Django 5.0.4 on 2024-04-27 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_cloud', '0006_remove_file_name_file_download_at_file_handle_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='handle',
            field=models.CharField(null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='url',
            field=models.CharField(),
        ),
    ]
