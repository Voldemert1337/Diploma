from django import forms
from .models import NewUsers, AddDebtorUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm





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


class DebtorRequestForm(forms.ModelForm):
    class Meta:
        model = AddDebtorUser
        fields = ['name', 'surname', 'amount', 'address', 'region', 'city', 'document']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'Имя дебитора',
            'surname': 'Фамилия дебитора',
            'amount': 'Сумма долга',
            'address': 'Адрес',
            'region': 'Регион',
            'city': 'Город',
            'document': 'Официальный документ',
        }

        def clean_amount(self):
            amount = self.cleaned_data.get('amount')
            if amount <= 0:
                raise forms.ValidationError('Сумма долга должна быть больше 0.')
            return amount

        def clean_document(self):
            document = self.cleaned_data.get('document')
            if not document:
                raise forms.ValidationError('Необходимо загрузить документ.')
            return document