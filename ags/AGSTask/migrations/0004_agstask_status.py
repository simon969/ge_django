# Generated by Django 4.0 on 2022-02-20 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AGSTask', '0003_alter_agsdocuments_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='agstask',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
