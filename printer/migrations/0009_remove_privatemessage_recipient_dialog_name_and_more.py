# Generated by Django 5.0.2 on 2024-06-11 08:36

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('printer', '0008_userprofile_telegram_id_dialog_privatemessage_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privatemessage',
            name='recipient',
        ),
        migrations.AddField(
            model_name='dialog',
            name='name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='privatemessage',
            name='dialog',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='printer.dialog'),
        ),
        migrations.AddField(
            model_name='privatemessage',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='privatemessage',
            name='sender',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
