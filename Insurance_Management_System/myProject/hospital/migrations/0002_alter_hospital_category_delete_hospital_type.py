# Generated by Django 4.2.5 on 2023-11-08 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='category',
            field=models.CharField(max_length=10),
        ),
        migrations.DeleteModel(
            name='Hospital_Type',
        ),
    ]