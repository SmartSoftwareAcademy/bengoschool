# Generated by Django 4.0.8 on 2023-05-20 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='code',
            field=models.CharField(default='2011', max_length=100),
        ),
    ]
