# Generated by Django 4.1.3 on 2022-11-22 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactions',
            name='category',
            field=models.CharField(max_length=200),
        ),
    ]
