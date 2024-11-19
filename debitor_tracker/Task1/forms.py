from django import forms
from .models import Region, City, NewUsers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm


class RegionCityForm(forms.Form):
    region = forms.ModelChoiceField(queryset=Region.objects.all(), label='Регион')
    city = forms.ModelChoiceField(queryset=City.objects.none(), label='Город')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['city'].queryset = City.objects.filter(region_id=region_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = self.instance.region.city_set.order_by('name')


class UserRegistrationForm(forms.ModelForm):
    # Добавляем поле для повторного ввода пароля
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
        label='Повторите пароль'  # Лейбл для поля повторного ввода пароля
    )

    class Meta:
        model = NewUsers  # Модель пользователя, которая будет использоваться
        fields = ['username', 'name', 'surname', 'age', 'email', 'password']  # Поля формы
        widgets = {
            # Настроим виджеты для полей формы
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'surname': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'age': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
        }
        labels = {
            # Лейблы для полей формы
            'username': 'Введите ваш Логин',
            'name': 'Введите ваше Имя',
            'surname': 'Введите вашу Фамилию',
            'age': 'Введите ваш возраст',
            'email': 'Введите вашу почту',
            'password': 'Введите пароль',
        }

    def clean_username(self):
        # Проверка на уникальность имени пользователя
        username = self.cleaned_data.get('username')
        if NewUsers.objects.filter(username=username).exists():  # Если имя уже существует в базе
            raise forms.ValidationError('Имя пользователя уже занято.')  # Генерация ошибки
        return username

    def clean_password(self):
        # Проверка пароля на соответствие требованиям
        password = self.cleaned_data.get('password')

        # Проверка минимальной длины пароля
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов.')

        # Используем встроенную проверку пароля, чтобы убедиться, что пароль соответствует требованиям безопасности
        try:
            validate_password(
                password)  # Это вызовет все стандартные проверки Django для пароля (например, проверку на слабые пароли)
        except ValidationError as e:
            raise forms.ValidationError(str(e))  # Если проверка не прошла, выводим ошибку

        return password

    def clean(self):
        # Проверка на совпадение паролей
        cleaned_data = super().clean()  # Сначала вызываем родительский метод для очистки данных

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('repeat_password')  # Получаем второй пароль из формы для подтверждения

        # Если пароли не совпадают, генерируем ошибку
        if password and password2 and password != password2:
            raise ValidationError('Пароли не совпадают.')

        return cleaned_data

    def clean_age(self):
        # Проверка возраста пользователя
        age = self.cleaned_data.get('age')

        # Возраст должен быть положительным числом и больше 18 лет
        if age <= 0:
            raise forms.ValidationError('Возраст должен быть положительным числом.')
        elif age < 18:
            raise forms.ValidationError('Вам должно быть более 18 лет.')  # Ошибка, если возраст меньше 18 лет

        return age


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем классы для полей
        self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg'})

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
