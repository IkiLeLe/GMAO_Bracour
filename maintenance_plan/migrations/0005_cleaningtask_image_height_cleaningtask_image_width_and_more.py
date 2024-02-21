# Generated by Django 4.2.9 on 2024-02-19 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance_plan', '0004_alter_cleaningtask_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cleaningtask',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cleaningtask',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lubrificationtask',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lubrificationtask',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='preventivetask',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='preventivetask',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cleaningtask',
            name='image',
            field=models.ImageField(blank=True, default=None, height_field='image_height', null=True, upload_to='images/', width_field='image_width'),
        ),
        migrations.AlterField(
            model_name='lubrificationtask',
            name='image',
            field=models.ImageField(blank=True, default=None, height_field='image_height', null=True, upload_to='images/', width_field='image_width'),
        ),
        migrations.AlterField(
            model_name='preventivetask',
            name='image',
            field=models.ImageField(blank=True, default=None, height_field='image_height', null=True, upload_to='images/', width_field='image_width'),
        ),
    ]
