# Generated by Django 4.2.2 on 2023-07-26 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0002_rename_amount_amountingridients_amountingridients'),
    ]

    operations = [
        migrations.RenameField(
            model_name='amountingridients',
            old_name='amountingridients',
            new_name='amount',
        ),
    ]
