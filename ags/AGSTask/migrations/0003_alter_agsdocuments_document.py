# Generated by Django 4.0 on 2022-02-18 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AGSTask', '0002_alter_agsdocuments_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agsdocuments',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='ags/documents/%Y/%m/%d'),
        ),
    ]
