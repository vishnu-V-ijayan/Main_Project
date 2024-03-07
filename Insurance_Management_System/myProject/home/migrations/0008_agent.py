# Generated by Django 4.2.5 on 2024-02-20 05:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('place', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('pin', models.CharField(max_length=6)),
                ('phone', models.CharField(max_length=10)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=10)),
                ('qualification', models.CharField(max_length=100)),
                ('aadhar', models.CharField(max_length=12, unique=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='agent_photos/')),
                ('registration_date', models.DateField()),
                ('staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agents', to='home.staff')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agents', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agent',
                'verbose_name_plural': 'Agents',
            },
        ),
    ]