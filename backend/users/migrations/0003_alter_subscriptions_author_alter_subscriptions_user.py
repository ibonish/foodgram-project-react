# Generated by Django 4.2.5 on 2023-09-28 06:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_subscriptions_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptions',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='subscriptions',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
    ]
