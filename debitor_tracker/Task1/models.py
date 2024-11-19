from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class NewUsersManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class NewUsers(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    password = models.CharField(max_length=128)
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


class Region(models.Model):
    name = models.CharField(max_length=100, verbose_name='Регион')

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100, verbose_name='Город')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name
