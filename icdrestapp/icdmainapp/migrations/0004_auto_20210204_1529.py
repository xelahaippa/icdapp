# Generated by Django 3.1.6 on 2021-02-04 15:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('icdmainapp', '0003_auto_20210204_1520'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='icdcode',
            unique_together=set(),
        ),
    ]
