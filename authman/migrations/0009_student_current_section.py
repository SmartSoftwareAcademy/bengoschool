# Generated by Django 4.0.8 on 2023-05-24 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0008_alter_schoolsetup_options_alter_classsection_name'),
        ('authman', '0008_remove_student_parent_mobile_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='current_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='academics.classsection'),
        ),
    ]
