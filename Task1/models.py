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
    """
    Менеджер для модели пользователей NewUsers.

    Этот класс предоставляет методы для создания пользователей и суперпользователей.
    Он наследует от BaseUserManager и переопределяет методы для нормализации email,
    хэширования пароля и установки значений по умолчанию для суперпользователей.

    Методы:
        create_user(username, email, password=None, **extra_fields):
            Создает и сохраняет обычного пользователя с указанным username, email и паролем.
            Параметры:
                username (str): Логин пользователя.
                email (str): Электронная почта пользователя.
                password (str, optional): Пароль пользователя.
                extra_fields (dict, optional): Дополнительные поля, которые нужно сохранить для пользователя.
            Возвращает:
                user (NewUsers): Созданный пользователь.

        create_superuser(username, email, password=None, **extra_fields):
            Создает и сохраняет суперпользователя с указанным username, email и паролем.
            Параметры:
                username (str): Логин суперпользователя.
                email (str): Электронная почта суперпользователя.
                password (str, optional): Пароль суперпользователя.
                extra_fields (dict, optional): Дополнительные поля для суперпользователя.
            Возвращает:
                user (NewUsers): Созданный суперпользователь.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        """
        Создает обычного пользователя.

        Параметры:
            username (str): Логин пользователя.
            email (str): Электронная почта пользователя.
            password (str, optional): Пароль пользователя.
            extra_fields (dict, optional): Дополнительные поля, которые нужно сохранить для пользователя.

        Возвращает:
            user (NewUsers): Созданный пользователь.

        Исключения:
            ValueError: Если email не указан.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Хэшируем пароль
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Создает суперпользователя.

        Параметры:
            username (str): Логин суперпользователя.
            email (str): Электронная почта суперпользователя.
            password (str, optional): Пароль суперпользователя.
            extra_fields (dict, optional): Дополнительные поля для суперпользователя.

        Возвращает:
            user (NewUsers): Созданный суперпользователь.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('age', 30)  # Значение по умолчанию
        return self.create_user(username, email, password, **extra_fields)


class NewUsers(AbstractBaseUser, PermissionsMixin):
    """
    Модель для пользователя системы.

    Этот класс наследует от AbstractBaseUser и PermissionsMixin, предоставляя базовую функциональность для модели пользователя,
    включая управление паролем, активностью, правами доступа и другие параметры.

    Атрибуты:
        username (str): Уникальное имя пользователя.
        name (str): Имя пользователя.
        surname (str): Фамилия пользователя.
        age (int): Возраст пользователя.
        email (str): Уникальная электронная почта пользователя.
        subscription (bool): Флаг подписки пользователя.
        subscription_end_date (datetime.date): Дата окончания подписки пользователя.
        created_at (datetime): Дата и время создания пользователя.
        updated_at (datetime): Дата и время последнего обновления пользователя.
        tg_account (str): Идентификатор аккаунта в Telegram.
        is_active (bool): Статус активности пользователя.
        is_staff (bool): Статус сотрудника (для прав доступа).

    Методы:
        full_name:
            Возвращает полное имя пользователя (имя и фамилия).
        has_valid_subscription:
            Проверяет, активна ли подписка пользователя.
        save(*args, **kwargs):
            Переопределяет метод сохранения, хэширует пароль перед сохранением.
        check_password(raw_password):
            Проверяет, совпадает ли введённый пароль с хэшированным паролем пользователя.
    """

    # Основные поля пользователя
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

    # Права доступа и активность
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Менеджер для создания пользователей
    objects = NewUsersManager()

    # Обязательные поля для аутентификации
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def full_name(self):
        """
        Возвращает полное имя пользователя, состоящее из имени и фамилии.

        Возвращает:
            str: Полное имя пользователя.
        """
        return f'{self.name} {self.surname}'

    @property
    def has_valid_subscription(self):
        """
        Проверяет, активна ли подписка у пользователя.

        Возвращает:
            bool: True, если подписка активна и не истекла; False в противном случае.
        """
        return self.subscription and self.subscription_end_date and self.subscription_end_date > timezone.now()

    def save(self, *args, **kwargs):
        """
        Переопределенный метод сохранения, который хэширует пароль перед сохранением.

        Если пароль не был предварительно захэширован, он будет захэширован с использованием метода make_password.
        Вызывается метод save() родительского класса после этого.

        Параметры:
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные именованные аргументы.
        """
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """
        Проверяет, совпадает ли введённый пароль с хэшированным паролем пользователя.

        Параметры:
            raw_password (str): Пароль, который необходимо проверить.

        Возвращает:
            bool: True, если пароли совпадают, иначе False.
        """
        return check_password(raw_password, self.password)


class Debtor(models.Model):
    """
    Модель для должников.

    Эта модель представляет должников, с которыми связан пользователь. Включает основную информацию о должнике,
    такую как имя, фамилия, сумма долга, адрес, регион и город. Также хранит временные метки для создания и изменения записи,
    а также уникальный индекс.

    Атрибуты:
        user (ForeignKey): Ссылка на пользователя (модель NewUsers), с которым связан должник.
        name (str): Имя должника.
        surname (str): Фамилия должника.
        amount (Decimal): Сумма долга должника.
        address (str): Адрес должника.
        region (str): Регион, в котором проживает должник.
        city (str): Город, в котором проживает должник.
        created_at (datetime): Дата и время создания записи о должнике.
        updated_at (datetime): Дата и время последнего изменения записи.
        index_key (int): Уникальный индекс, присваиваемый каждому должнику.

    Методы:
        None (это просто модель без дополнительных методов, кроме стандартных методов Django)
    """

    # Ссылка на пользователя
    user = models.ForeignKey(NewUsers, on_delete=models.CASCADE, verbose_name='Пользователь')

    # Личные данные должника
    name = models.CharField(max_length=100, verbose_name='Имя должника')
    surname = models.CharField(max_length=100, verbose_name='Фамилия должника')

    # Долг и местоположение должника
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма долга')
    address = models.CharField(max_length=100, verbose_name='Адрес должника')
    region = models.CharField(max_length=100, verbose_name='Регион')
    city = models.CharField(max_length=100, verbose_name='Город')

    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    # Уникальный индекс
    index_key = models.IntegerField(null=True, verbose_name='Индекс', unique=True)


class AddDebtorUser(models.Model):
    """
    Модель для добавления должников в систему.

    Эта модель используется для создания и обработки запросов на добавление должников. Каждый должник связан с
    конкретным пользователем и имеет статус, который отражает текущую стадию обработки его данных (например, "в обработке", "одобрено").
    Модель также включает атрибуты для хранения персональных данных должника, информации о долге, а также документов, связанных с
    процессом добавления и удаления.

    Атрибуты:
        STATUS_CHOICES (list): Список возможных статусов для должника, таких как 'pending', 'approved', 'added' и другие.
        user (ForeignKey): Ссылка на пользователя (модель NewUsers), с которым связан данный должник.
        name (str): Имя должника.
        surname (str): Фамилия должника.
        amount (Decimal): Сумма долга должника.
        address (str): Адрес должника.
        region (str): Регион, в котором проживает должник.
        city (str): Город, в котором проживает должник.
        created_at (datetime): Дата и время создания записи о должнике.
        updated_at (datetime): Дата и время последнего обновления записи.
        status (str): Статус запроса на добавление должника. Статус управляется через выбор из STATUS_CHOICES.
        document (FileField): Документ, связанный с запросом.
        index_key (int): Уникальный индекс для записи должника.
        deletion_reason (str): Причина удаления должника (если применимо).
        deletion_document (FileField): Документ, подтверждающий удаление (если применимо).

    Методы:
        __str__: Возвращает строковое представление записи, показывающее имя, фамилию и статус должника.
        approve_and_transfer_to_debtor: Меняет статус на 'Одобрено' и переносит данные в основную таблицу Debtor.
    """

    # Список возможных статусов для должника
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

    # Атрибуты модели, хранящие данные о должнике
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
    deletion_reason = models.TextField(null=True, blank=True, verbose_name='Причина удаления')
    deletion_document = models.FileField(upload_to='deletion_documents/', null=True, blank=True,
                                         verbose_name='Документ удаления')

    def __str__(self):
        """
        Возвращает строковое представление записи о должнике.

        Возвращает строку, содержащую имя, фамилию и текущий статус должника.

        Returns:
            str: Строка с информацией о должнике.
        """
        return f"{self.name} {self.surname} - {self.get_status_display()}"

    def approve_and_transfer_to_debtor(self):
        """
        Одобряет заявку на добавление должника и переносит его данные в основную таблицу Debtor.

        Изменяет статус записи на 'added' и переносит данные должника в таблицу Debtor. Если операция
        проходит успешно, статус должника обновляется, и в лог записывается успешное добавление.

        Returns:
            Debtor: Объект созданного должника в таблице Debtor.

        Логирует процесс добавления должника в основную таблицу.
        """
        logger.info(f"Начинаем перенос данных для {self.name} {self.surname} в таблицу Debtor.")
        debtor = Debtor.objects.create(
            user=self.user,
            name=self.name,
            surname=self.surname,
            amount=self.amount,
            address=self.address,
            region=self.region,
            city=self.city,
        )
        self.status = 'added'
        self.save()
        logger.info(f"Дебитор {self.name} {self.surname} успешно добавлен в таблицу Debtor.")
        return debtor


@receiver(pre_save, sender=AddDebtorUser)
def set_index_key(sender, instance, **kwargs):
    """
    Генерирует уникальный index_key для нового объекта AddDebtorUser.

    Эта функция срабатывает перед сохранением нового объекта модели AddDebtorUser. Она проверяет, является ли
    объект новым (не имеющим первичного ключа `pk`). Если объект новый, функция генерирует уникальный `index_key`,
    основываясь на максимальном значении `index_key` среди существующих записей. Если в базе нет записей, то
    присваивает значение `1`.

    Аргументы:
        sender (Model): Модель, которая отправила сигнал (в данном случае AddDebtorUser).
        instance (AddDebtorUser): Экземпляр объекта, для которого генерируется уникальный `index_key`.
        **kwargs: Дополнительные параметры сигнала (не используются).

    Примечание:
        Генерация уникального ключа осуществляется на основе максимального значения существующего ключа.
        Это гарантирует, что новые объекты всегда получат уникальный индекс.
    """
    if instance.pk is None:  # Новый объект
        last_debtor = AddDebtorUser.objects.aggregate(Max('index_key'))['index_key__max']
        instance.index_key = 1 if last_debtor is None else last_debtor + 1
