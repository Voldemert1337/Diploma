# Generated by Django 5.1.3 on 2024-11-20 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task1', '0004_adddebtoruser_deletion_document_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adddebtoruser',
            name='index_key',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='Индекс'),
        ),
        migrations.AddField(
            model_name='debtor',
            name='index_key',
            field=models.IntegerField(null=True, unique=True, verbose_name='индекс'),
        ),
    ]