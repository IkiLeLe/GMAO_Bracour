# Generated by Django 4.2.9 on 2024-01-25 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance_plan', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preventivetask',
            name='part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance_plan.part'),
        ),
    ]
