# Generated by Django 5.1.2 on 2024-12-13 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='followers',
            new_name='following',
        ),
    ]