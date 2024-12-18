# Generated by Django 5.1.3 on 2024-11-20 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task1', '0003_alter_newusers_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='adddebtoruser',
            name='deletion_document',
            field=models.FileField(blank=True, null=True, upload_to='deletion_documents/', verbose_name='Документ удаления'),
        ),
        migrations.AddField(
            model_name='adddebtoruser',
            name='deletion_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Причина удаления'),
        ),
        migrations.AlterField(
            model_name='adddebtoruser',
            name='status',
            field=models.CharField(choices=[('pending', 'В обработке'), ('approved', 'Одобрено'), ('added', 'Добавлено в базу'), ('rejected', 'Отклонено'), ('deleting', 'Удаляется'), ('deleted', 'Удалено')], default='pending', max_length=20, verbose_name='Статус'),
        ),
    ]
