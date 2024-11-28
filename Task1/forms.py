from django import forms
from .models import NewUsers, AddDebtorUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm


class UserRegistrationForm(forms.ModelForm):
    """
    Форма регистрации нового пользователя.

    Эта форма используется для регистрации пользователей, включая поля для логина, имени, фамилии,
    возраста, электронной почты и пароля. Также добавлено поле для повторного ввода пароля для
    проверки правильности ввода.

    Атрибуты:
        repeat_password (forms.CharField): Поле для повторного ввода пароля, используется для
                                            подтверждения правильности введённого пароля.
    """

    # Поле для повторного ввода пароля
    repeat_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
        label='Повторите пароль'
    )

    class Meta:
        """
        Метаданные для формы.

        Указывает модель и поля, которые должны быть использованы в форме.
        Также настраиваются виджеты и метки для каждого поля.
        """
        model = NewUsers
        fields = ['username', 'name', 'surname', 'age', 'email', 'password']

        # Настройка виджетов для полей
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'surname': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'age': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
        }

        # Настройка меток для полей
        labels = {
            'username': 'Введите ваш Логин',
            'name': 'Введите ваше Имя',
            'surname': 'Введите вашу Фамилию',
            'age': 'Введите ваш возраст',
            'email': 'Введите вашу почту',
            'password': 'Введите пароль',
        }

    def clean_username(self):
        """
        Валидирует поле 'username' формы.

        Проверяет, существует ли уже в базе данных пользователь с таким же именем. Если имя
        пользователя занято, выбрасывается ошибка валидации.

        Returns:
            str: Проверенное имя пользователя.

        Raises:
            forms.ValidationError: Если имя пользователя уже занято.
        """
        username = self.cleaned_data.get('username')
        if NewUsers.objects.filter(username=username).exists():
            raise forms.ValidationError('Имя пользователя уже занято.')
        return username

    def clean_password(self):
        """
        Валидирует поле 'password' формы.

        Проверяет, что пароль содержит минимум 8 символов. Также применяет стандартную
        валидацию пароля, проверяя его безопасность.

        Returns:
            str: Проверенный пароль.

        Raises:
            forms.ValidationError: Если пароль слишком короткий или не соответствует требованиям безопасности.
        """
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError('Пароль должен содержать минимум 8 символов.')

        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError(str(e))

        return password

    def clean(self):
        """
        Валидирует всю форму, проверяя соответствие пароля и повторного пароля.

        Проверяет, что значение поля 'password' совпадает с значением поля 'repeat_password'.
        Если пароли не совпадают, выбрасывается ошибка валидации.

        Returns:
            dict: Очищенные данные формы.

        Raises:
            ValidationError: Если пароли не совпадают.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('repeat_password')

        if password and password2 and password != password2:
            raise ValidationError('Пароли не совпадают.')

        return cleaned_data

        def clean_age(self):
            """
            Валидирует поле 'age' формы.

            Проверяет, что возраст является положительным числом и что пользователю
            более 18 лет. Если возраст меньше или равен нулю, либо меньше 18 лет,
            выбрасывается ошибка валидации.

            Returns:
                int: Проверенный возраст.

            Raises:
                forms.ValidationError: Если возраст отрицателен или меньше 18 лет.
            """
            age = self.cleaned_data.get('age')
            if age <= 0:
                raise forms.ValidationError('Возраст должен быть положительным числом.')
            if age < 18:
                raise forms.ValidationError('Вам должно быть более 18 лет.')
            return age

    class CustomAuthenticationForm(AuthenticationForm):
        """
        Кастомная форма для аутентификации пользователя.

        Эта форма наследуется от стандартной `AuthenticationForm` и обновляет виджеты для полей
        'username' и 'password', чтобы они использовали более крупные стили для ввода.
        """

        def __init__(self, *args, **kwargs):
            """
            Инициализирует кастомную форму аутентификации, обновляя виджеты полей.

            Обновляет виджеты для полей 'username' и 'password' с использованием CSS классов для
            улучшенного визуального отображения.

            Args:
                *args: Аргументы для инициализации родительского класса.
                **kwargs: Ключевые аргументы для инициализации родительского класса.
            """
            super().__init__(*args, **kwargs)
            self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg'})
            self.fields['password'].widget.attrs.update({'class': 'form-control form-control-lg'})


class LoginForm(forms.Form):
    """
    Форма для аутентификации пользователя.

    Содержит два поля: 'username' для ввода логина и 'password' для ввода пароля.
        """
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class DebtorRequestForm(forms.ModelForm):
    """
    Форма для создания запроса на добавление дебитора.

    Эта форма используется для сбора данных о дебиторе, включая его имя, фамилию,
    сумму долга, адрес и другие важные сведения, а также для загрузки документа,
    подтверждающего долг.
    """

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
        """
        Валидирует поле 'amount' формы.

        Проверяет, что сумма долга больше нуля. Если сумма отрицательная или равна нулю,
        выбрасывается ошибка валидации.

        Returns:
            Decimal: Проверенная сумма долга.

        Raises:
            forms.ValidationError: Если сумма долга меньше или равна нулю.
        """
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Сумма долга должна быть больше 0.')
        return amount

    def clean_document(self):
        """
        Валидирует поле 'document' формы.

        Проверяет, что документ был загружен. Если документ отсутствует, выбрасывается ошибка
        валидации, требующая загрузки документа.

        Returns:
            file: Загрузленный документ.

        Raises:
            forms.ValidationError: Если документ не был загружен.
        """
        document = self.cleaned_data.get('document')
        if not document:
            raise forms.ValidationError('Необходимо загрузить документ.')
        return document


class DeletionRequestForm(forms.Form):
    """
    Форма для отправки запроса на удаление дебитора.

    Поля:
    - reason: Причина удаления дебитора (обязательное поле).
    - document: Загружаемый документ (необязательное поле).
    """

    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Укажите причину удаления'}),
        required=True
    )
    document = forms.FileField(required=False)
