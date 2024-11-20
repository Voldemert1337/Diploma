from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm, DebtorRequestForm, DeletionRequestForm
from .models import Debtor, AddDebtorUser, NewUsers
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation



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


@login_required
def personal_cabinet(request):
    requests = AddDebtorUser.objects.filter(user=request.user)
    return render(request, 'first/personalAccount.html', {'requests': requests})

@login_required
def add_request(request):
    if request.method == 'POST':
        form = DebtorRequestForm(request.POST, request.FILES)
        if form.is_valid():
            debtor_request = form.save(commit=False)
            debtor_request.user = request.user
            debtor_request.save()
            return redirect('personal_cabinet')
    else:
        form = DebtorRequestForm()
    return render(request, 'add_request.html', {'form': form})

@login_required
def edit_request(request, pk):
    debtor_request = get_object_or_404(AddDebtorUser, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DebtorRequestForm(request.POST, request.FILES, instance=debtor_request)
        if form.is_valid():
            form.save()
            return redirect('personal_cabinet')
    else:
        form = DebtorRequestForm(instance=debtor_request)
    return render(request, 'edit_request.html', {'form': form})

@login_required
def delete_request(request, pk):
    debtor_request = get_object_or_404(AddDebtorUser, pk=pk, user=request.user)
    if request.method == 'POST':
        debtor_request.delete()
        return redirect('personal_cabinet')
    return render(request, 'delete_request.html', {'request_obj': debtor_request})


@login_required
def update_telegram(request):
    """
    Обработчик обновления Telegram-аккаунта пользователя.
    """
    if request.method == 'POST':
        # Получаем новое значение Telegram из запроса
        telegram = request.POST.get('telegram')

        # Проверяем, что значение не пустое
        if telegram:
            # Обновляем поле tg_account у текущего пользователя
            request.user.tg_account = telegram
            request.user.save()

            # Добавляем сообщение об успешном обновлении
            messages.success(request, 'Ваш Telegram успешно обновлен!')
        else:
            # Если поле пустое, отправляем сообщение об ошибке
            messages.error(request, 'Поле Telegram не может быть пустым.')

        # Перенаправляем обратно на страницу личного кабинета
        return redirect('personal_cabinet')  # Убедитесь, что это имя вашей страницы

    # Если метод не POST, перенаправляем обратно на личный кабинет
    return redirect('personal_cabinet')

@login_required
def update_full_name(request):
    """
        Обработчик обновления Имени и фамилии-аккаунта пользователя.
    """
    if request.method == 'POST':
        # Получаем новое значение Имени и Фамилии из запроса
        name = request.POST.get('name')
        surname = request.POST.get('surname')

        # Проверяем, что значение не пустое
        if name and surname:
            # Обновляем поле tg_account у текущего пользователя
            request.user.name = name
            request.user.surname = surname
            request.user.save()

            # Добавляем сообщение об успешном обновлении
            messages.success(request, 'Ваши Имя и Фамилия успешно обновлен!')
        else:
            # Если поле пустое, отправляем сообщение об ошибке
            messages.error(request, 'Поле Имя и Фамилия не может быть пустым.')

        # Перенаправляем обратно на страницу личного кабинета
        return redirect('personal_cabinet')  # Убедитесь, что это имя вашей страницы

    # Если метод не POST, перенаправляем обратно на личный кабинет
    return redirect('personal_cabinet')



@login_required
def update_email(request):
    """
    Обработчик обновления email-аккаунта пользователя.
    """
    if request.method == 'POST':
        # Получаем новое значение email из запроса
        email = request.POST.get('email')

        # Проверяем, что значение не пустое
        if email:
            # Проверяем, существует ли уже пользователь с таким email
            if NewUsers.objects.filter(email=email).exists():
                # Если email уже используется, отправляем сообщение об ошибке
                messages.error(request, 'Этот Email уже зарегистрирован другим пользователем.')
            else:
                # Обновляем поле email у текущего пользователя
                request.user.email = email
                request.user.save()

                # Добавляем сообщение об успешном обновлении
                messages.success(request, 'Ваш Email успешно обновлен!')
        else:
            # Если поле пустое, отправляем сообщение об ошибке
            messages.error(request, 'Поле Email не может быть пустым.')

        # Перенаправляем обратно на страницу личного кабинета
        return redirect('personal_cabinet')  # Убедитесь, что это имя вашей страницы

    # Если метод не POST, перенаправляем обратно на личный кабинет
    return redirect('personal_cabinet')


@login_required
def add_debtor(request):
    """
    Обработчик для добавления дебитора.
    """
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        amount = request.POST.get('amount')
        address = request.POST.get('address')
        region = request.POST.get('region')
        city = request.POST.get('city')
        document = request.FILES.get('document')

        # Проверка на обязательность всех полей
        if name and surname and amount and address and region and city and document:
            # Создаем новый объект AddDebtorUser
            AddDebtorUser.objects.create(
                user=request.user,  # Привязываем к текущему пользователю
                name=name,
                surname=surname,
                amount=amount,
                address=address,
                region=region,
                city=city,
                document=document,
                status='pending',  # Статус "В обработке"
                # index_key назначается автоматически в сигнале
            )
            messages.success(request, 'Дебитор успешно добавлен!')
        else:
            messages.error(request, 'Все поля обязательны для заполнения.')

        # Перенаправляем на страницу личного кабинета или на другую страницу
        return redirect('personal_cabinet')  # Замените на правильное имя вашего URL

    # Если это GET запрос, просто перенаправляем на личный кабинет
    else:
        return redirect('personal_cabinet')  # Перенаправление для запросов GET


@login_required
def edit_debtor(request, debtor_id):
    """
    Обработчик для редактирования данных дебитора.
    """
    if request.method == 'POST':
        # Получаем данные из запроса
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        amount = request.POST.get('amount')
        address = request.POST.get('address')
        region = request.POST.get('region')
        city = request.POST.get('city')
        document = request.FILES.get('document')
        update_description = request.POST.get('update_description')  # Описание изменений
        status = 'update_requested'  # Статус обновления
        created_at = request.POST.get('created_at')

        # Находим дебитора по ID
        try:
            debtor = AddDebtorUser.objects.get(id=debtor_id, user=request.user)
        except AddDebtorUser.DoesNotExist:
            messages.error(request, "Дебитор не найден.")
            return redirect('personal_cabinet')

        # Обновляем данные, только если они были переданы в запросе
        if name:
            debtor.name = name
        if surname:
            debtor.surname = surname

        if amount:
            try:
                # Заменяем запятую на точку, если она есть
                amount = amount.replace(',', '.')
                # Преобразуем строку в Decimal
                debtor.amount = Decimal(amount)
            except (InvalidOperation, ValueError):
                # Если преобразование не удалось, отправляем ошибку
                messages.error(request, "Неверный формат суммы.")
                return redirect('personal_cabinet')

        if address:
            debtor.address = address
        if region:
            debtor.region = region
        if city:
            debtor.city = city
        if update_description:  # Если описание изменений есть
            debtor.update_description = update_description
        if document:  # Если есть новый документ
            debtor.document = document
        if created_at:
            debtor.created_at = created_at

        # Устанавливаем статус на "На обновление"
        debtor.status = status

        debtor.save()  # Сохраняем изменения

        messages.success(request, 'Дебитор успешно обновлен! Ожидайте подтверждения от администратора.')
        return redirect('personal_cabinet')  # Перенаправляем после успешного редактирования

    else:
        return redirect('personal_cabinet')  # Для GET запроса, возвращаем на личный кабинет



@login_required
def request_deletion(request, debtor_id):
    """
    Обработчик для запроса на удаление дебитора.
    """
    try:
        # Находим дебитора по ID и текущему пользователю
        debtor = get_object_or_404(AddDebtorUser, id=debtor_id, user=request.user)

        if request.method == 'POST':
            # Если форма отправлена, обрабатываем данные
            form = DeletionRequestForm(request.POST, request.FILES)

            if form.is_valid():
                # Сохраняем причину удаления и документ
                debtor.deletion_reason = form.cleaned_data['reason']
                debtor.deletion_document = form.cleaned_data.get('document')
                debtor.status = 'deleting'  # Меняем статус на 'Удаляется'
                debtor.save()

                messages.success(request, 'Запрос на удаление успешно отправлен!')
                return redirect('personal_cabinet')  # Перенаправляем на личный кабинет
            else:
                messages.error(request, 'Ошибка при отправке запроса. Пожалуйста, попробуйте снова.')

        else:
            # В случае GET-запроса, просто показываем сообщение
            messages.info(request, 'Запрос на удаление дебитора')

    except Debtor.DoesNotExist:
        messages.error(request, 'Дебитор не найден.')

    return redirect('personal_cabinet')  # Перенаправляем обратно на личный кабинет

def confirm_deletion(request, debtor_id):
    debtor = get_object_or_404(Debtor, id=debtor_id)

    # Проверяем, что статус "Удаляется" перед удалением
    if debtor.status == 'deleting':
        # Выполняем удаление записи
        debtor.status = 'deleted'  # Меняем статус на "Удален"
        debtor.save()
        debtor.delete()  # Удаляем запись из базы данных
        return redirect('admin:app_debtor_changelist')  # Админский список должников
    else:
        # Если статус не "deleting", значит нельзя подтвердить удаление
        return redirect('admin:app_debtor_changelist')
