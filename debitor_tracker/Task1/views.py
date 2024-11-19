from django.shortcuts import render, redirect
from .forms import RegionCityForm
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm
from .models import Debtor
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash



def index(request):
    return render(request, 'first/index.html')

def register(request):
    return render(request, 'first/register.html')

def login(request):
    return render(request, 'first/login.html')

def table(request):
    return render(request, 'first/table.html')




def get_debtors(request):
    debtors = Debtor.objects.all().values('name', 'surname', 'amount', 'address', 'region', 'city', 'created_at', 'updated_at')
    debtor_list = list(debtors)  # Преобразуем QuerySet в список словарей
    return JsonResponse({'debtors': debtor_list})






def user_register(request):
    # Проверяем, что запрос был отправлен методом POST
    if request.method == 'POST':
        # Создаем экземпляр формы с данными из POST-запроса
        form = UserRegistrationForm(request.POST)

        # Проверяем, что форма прошла валидацию
        if form.is_valid():
            # Создаем нового пользователя, но пока не сохраняем его в базе данных (commit=False)
            user = form.save(commit=False)

            # Шифруем пароль перед сохранением в базе данных
            user.password = make_password(form.cleaned_data['password'])

            # Сохраняем пользователя в базе данных
            user.save()

            # Входим в систему с данным пользователем
            auth_login(request, user)  # Вход в систему сразу после регистрации

            # Выводим сообщение об успешной регистрации и входе
            messages.success(request, 'Ваш аккаунт был создан и вы автоматически вошли в систему.')

            # Перенаправляем на главную страницу или любую другую
            return redirect('index')  # Перенаправляем пользователя на главную страницу

        else:
            # Если форма невалидна, выводим ошибки
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        # Если запрос не POST (например, GET), создаем пустую форму для отображения на странице
        form = UserRegistrationForm()

    # Отправляем форму в шаблон для отображения на странице
    return render(request, 'first/register.html', {'form': form})



def login_view(request):
    # Проверяем, что запрос был отправлен методом POST
    if request.method == 'POST':
        # Создаем экземпляр формы с данными из POST-запроса
        form = LoginForm(request.POST)

        # Проверяем, что форма прошла валидацию
        if form.is_valid():
            # Извлекаем имя пользователя и пароль из очищенных данных формы
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(f"Username: {username}, Password: {password}")  # Отладка: выводим введенные данные

            # Пытаемся аутентифицировать пользователя с введенными данными
            user = authenticate(request, username=username, password=password)

            # Если аутентификация успешна (пользователь найден)
            if user is not None:
                # Входим в систему, используя пользователя (используем псевдоним auth_login для предотвращения конфликтов)
                auth_login(request, user)

                # Перенаправляем пользователя на главную страницу (или страницу после успешного входа)
                return redirect('index')  # Замените 'index' на имя вашей страницы
            else:
                # Если аутентификация не удалась, выводим сообщение об ошибке
                messages.error(request, 'Неправильное имя пользователя или пароль.')
        else:
            # Если форма не прошла валидацию, выводим сообщение об ошибке
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        # Если запрос не POST (например, GET), создаем пустую форму для отображения на странице
        form = LoginForm()

    # Отправляем форму в шаблон для отображения на странице
    return render(request, 'first/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')




def change_password(request):
    # Если пользователь не авторизован, перенаправляем его на страницу входа
    if not request.user.is_authenticated:
        return redirect('login')

    # Если запрос POST, значит пользователь отправил форму
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        print(f"Данные формы: {request.POST}")  # Отладка

        # Проверяем, что форма валидна
        if form.is_valid():
            print("Форма валидна.")  # Отладка
            # Сохраняем новый пароль
            form.save()

            # Обновляем сессию пользователя, чтобы новый пароль стал активным
            update_session_auth_hash(request, form.user)
            print("Пароль обновлен, сессия пользователя обновлена.")  # Отладка

            # Отправляем сообщение об успешной смене пароля
            messages.success(request, 'Ваш пароль был успешно изменен.')

            # Перенаправляем на главную страницу или любую другую
            return redirect('index')
        else:
            print("Форма невалидна. Ошибки формы:")  # Отладка
            for field, errors in form.errors.items():  # Отладка ошибок
                print(f"Поле: {field}, Ошибки: {errors}")

            # Если форма невалидна, показываем сообщение об ошибке
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

    else:
        form = PasswordChangeForm(user=request.user)

    # Отображаем страницу с формой смены пароля
    return render(request, 'first/change_password.html', {'form': form})


def table_view(request):
    debtors = Debtor.objects.all()  # Загружаем всех должников из базы
    print(debtors)  # Для отладки: выводим записи в консоль
    return render(request, 'first/table.html', {'debtors': debtors})
