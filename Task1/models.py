from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import Max

# Настроим логирование
logger = logging.getLogger(__name__)



class NewUsersManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Хэшируем пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('age', 30)  # Установите значение по умолчанию
        return self.create_user(username, email, password, **extra_fields)


class NewUsers(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    email = models.EmailField(unique=True)
    subscription = models.BooleanField(default=False)
    subscription_end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tg_account = models.CharField(max_length=33)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = NewUsersManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def full_name(self):
        return f'{self.name} {self.surname}'

    @property
    def has_valid_subscription(self):
        return self.subscription and self.subscription_end_date and self.subscription_end_date > timezone.now()

    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Debtor(models.Model):
    # Должники
    user = models.ForeignKey(NewUsers, on_delete=models.CASCADE, verbose_name='Пользователь')
    name = models.CharField(max_length=100, verbose_name='Имя должника')
    surname = models.CharField(max_length=100, verbose_name='Фамилия должника')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма долга')
    address = models.CharField(max_length=100, verbose_name='адресс должника')
    region = models.CharField(max_length=100, verbose_name='регион')
    city = models.CharField(max_length=100, verbose_name='город')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    index_key = models.IntegerField(null=True, verbose_name='индекс',unique=True)

class AddDebtorUser(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('approved', 'Одобрено'),
        ('added', 'Добавлено в базу'),
        ('rejected', 'Отклонено'),
        ('deleting', 'Удаляется'),
        ('deleted', 'Удалено'),
        ('update_requested', 'Запрос на обновление'),
        ('under_review', 'На проверке'),
        ('approved_for_update', 'Одобрено для обновления'),
        ('updated_in_db', 'Обновлено в базе')
    ]

    user = models.ForeignKey(NewUsers, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=255, verbose_name="Имя дебитора")
    surname = models.CharField(max_length=255, verbose_name="Фамилия дебитора")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма долга")
    address = models.TextField(verbose_name="Адрес")
    region = models.CharField(max_length=255, verbose_name="Регион")
    city = models.CharField(max_length=255, verbose_name="Город")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    document = models.FileField(upload_to='documents/', verbose_name="Документ")
    index_key = models.IntegerField(unique=True, verbose_name="Индекс", null=True, blank=True)

    # Причина удаления и документ
    deletion_reason = models.TextField(null=True, blank=True, verbose_name='Причина удаления')
    deletion_document = models.FileField(upload_to='deletion_documents/', null=True, blank=True, verbose_name='Документ удаления')

    def __str__(self):
        return f"{self.name} {self.surname} - {self.get_status_display()}"




    def approve_and_transfer_to_debtor(self):
        """Метод для изменения статуса на 'Одобрено' и переноса в основную таблицу"""
        logger.info(f"Начинаем перенос данных для {self.name} {self.surname} в таблицу Debtor.")
        # Переносим данные в Debtor
        debtor = Debtor.objects.create(
            user=self.user,
            name=self.name,
            surname=self.surname,
            amount=self.amount,
            address=self.address,
            region=self.region,
            city=self.city,

        )

        # После успешного добавления в основную таблицу, меняем статус на 'added'
        self.status = 'added'
        self.save()
        logger.info(f"Дебитор {self.name} {self.surname} успешно добавлен в таблицу Debtor.")
        return debtor


# Сигнал для автоматической генерации уникального index_key
@receiver(pre_save, sender=AddDebtorUser)
def set_index_key(sender, instance, **kwargs):
    """
    Этот сигнал автоматически присваивает уникальный index_key
    при создании нового объекта AddDebtorUser.
    """
    if instance.pk is None:  # Если объект новый
        # Получаем максимальное значение index_key среди существующих записей
        last_debtor = AddDebtorUser.objects.aggregate(Max('index_key'))['index_key__max']

        # Если в базе нет записей, начинаем с 1
        if last_debtor is None:
            instance.index_key = 1
        else:
            instance.index_key = last_debtor + 1
