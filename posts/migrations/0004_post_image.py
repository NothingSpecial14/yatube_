# Generated by Django 4.2.3 on 2023-09-03 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_post_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posts/'),
        ),
    ]