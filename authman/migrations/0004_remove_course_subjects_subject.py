# Generated by Django 4.0.8 on 2023-05-20 23:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authman', '0003_course_subjects'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='subjects',
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authman.course')),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authman.staff')),
            ],
        ),
    ]
