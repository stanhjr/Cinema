# Generated by Django 3.2.9 on 2022-01-22 14:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cinema', '0007_tokenexpired'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchasedticket',
            name='purchase_amount',
        ),
    ]
