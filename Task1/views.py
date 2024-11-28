import logging
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

# Логирование для отслеживания действий
logger = logging.getLogger(__name__)


def index(request):
    """
    Отображает главную страницу сайта.

    Эта функция обрабатывает запрос на главную страницу, записывает информацию в лог
    о доступе к главной странице и возвращает HTML-шаблон главной страницы.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о запросе пользователя.

    Возвращает:
        HttpResponse: Ответ, содержащий отрендеренную главную страницу сайта.
    """
    logger.info("Доступ к главной странице.")
    # Отображение главной страницы сайта
    return render(request, 'first/index.html')


def register(request):
    """
    Отображает страницу регистрации.

    Эта функция обрабатывает запрос на страницу регистрации, записывает информацию в лог
    о доступе к странице регистрации и возвращает HTML-шаблон страницы регистрации.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о запросе пользователя.

    Возвращает:
        HttpResponse: Ответ, содержащий отрендеренную страницу регистрации.
    """
    logger.info("Доступ к странице регистрации.")
    # Отображение страницы регистрации
    return render(request, 'first/register.html')


def login(request):
    """
    Отображает страницу входа.

    Эта функция обрабатывает запрос на страницу входа, записывает информацию в лог
    о доступе к странице входа и возвращает HTML-шаблон страницы входа.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о запросе пользователя.

    Возвращает:
        HttpResponse: Ответ, содержащий отрендеренную страницу входа.
    """
    logger.info("Доступ к странице входа.")
    # Отображение страницы входа
    return render(request, 'first/login.html')


def table(request):
    """
    Отображает страницу с таблицей.

    Эта функция обрабатывает запрос на страницу с таблицей, записывает информацию в лог
    о доступе к странице с таблицей и возвращает HTML-шаблон страницы с таблицей.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о запросе пользователя.

    Возвращает:
        HttpResponse: Ответ, содержащий отрендеренную страницу с таблицей.
    """
    logger.info("Доступ к странице с таблицей.")
    # Отображение страницы с таблицей (например, дебиторов)
    return render(request, 'first/table.html')


def get_debtors(request):
    """
    Получает данные о всех дебиторах и возвращает их в формате JSON.

    Эта функция извлекает информацию о дебиторах из базы данных, включая их имя, фамилию,
    сумму долга, адрес, регион, город, а также дату создания и обновления. Данные затем
    преобразуются в список словарей и отправляются в ответе в формате JSON.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о запросе пользователя.

    Возвращает:
        JsonResponse: Ответ с данными о дебиторах в формате JSON, включающий информацию о каждом дебиторе.
    """
    logger.info("Получение данных о дебиторах.")
    # Получение всех дебиторов и их информации
    debtors = Debtor.objects.all().values(
        'name', 'surname', 'amount', 'address', 'region', 'city', 'created_at', 'updated_at'
    )
    debtor_list = list(debtors)  # Преобразуем QuerySet в список словарей
    logger.info(f"Данные о дебиторах получены: {debtor_list}")
    # Возвращаем информацию о дебиторах в формате JSON
    return JsonResponse({'debtors': debtor_list})


def user_register(request):
    """
    Обрабатывает процесс регистрации нового пользователя.

    Эта функция управляет процессом регистрации нового пользователя:
    отображает форму регистрации, проверяет её на валидность, создает нового пользователя,
    хеширует пароль, выполняет вход пользователя после успешной регистрации и
    перенаправляет на главную страницу. Если форма содержит ошибки, пользователю выводится сообщение об ошибке.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий данные формы и информацию о запросе пользователя.

    Возвращает:
        HttpResponseRedirect: Перенаправляет пользователя на главную страницу после успешной регистрации.
        Или возвращает страницу с формой регистрации в случае ошибок валидации.
    """
    logger.info("Начало процесса регистрации пользователя.")
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создание нового пользователя
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)  # Автоматический вход после регистрации
            messages.success(request, 'Ваш аккаунт был создан и вы автоматически вошли в систему.')
            logger.info(f"Пользователь {user.username} успешно зарегистрирован.")
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            logger.warning(f"Ошибка при регистрации: {form.errors}")
    else:
        form = UserRegistrationForm()
    return render(request, 'first/register.html', {'form': form})


def login_view(request):
    """
    Обрабатывает процесс входа пользователя.

    Эта функция управляет процессом аутентификации пользователя:
    отображает форму входа, проверяет её на валидность, а также выполняет вход пользователя,
    если введены правильные данные (имя пользователя и пароль). В случае ошибки
    входа или если форма имеет ошибки, пользователю выводится соответствующее сообщение.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий данные формы и информацию о запросе пользователя.

    Возвращает:
        HttpResponseRedirect: Перенаправляет пользователя на главную страницу после успешного входа.
        Или возвращает страницу с формой входа в случае ошибок аутентификации или валидации формы.
    """
    logger.info("Начало процесса входа пользователя.")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                logger.info(f"Пользователь {username} успешно вошёл в систему.")
                return redirect('index')
            else:
                messages.error(request, 'Неправильное имя пользователя или пароль.')
                logger.warning(f"Неудачная попытка входа для {username}")
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            logger.warning(f"Ошибка при входе: {form.errors}")
    else:
        form = LoginForm()
    return render(request, 'first/login.html', {'form': form})


def logout_view(request):
    """
    Обрабатывает процесс выхода пользователя из системы.

    Эта функция завершает сессию пользователя и перенаправляет его на главную страницу.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем пользователе.

    Возвращает:
        HttpResponseRedirect: Перенаправляет пользователя на главную страницу после выхода из системы.
    """
    logger.info("Пользователь вышел из системы.")
    logout(request)
    return redirect('index')


def change_password(request):
    """
    Обрабатывает процесс изменения пароля для аутентифицированного пользователя.

    Эта функция позволяет пользователю изменить свой пароль. После успешного изменения пароля
    обновляется сессия пользователя, и ему показывается сообщение об успешном изменении пароля.
    В случае ошибок форма будет отображена снова с соответствующими сообщениями об ошибке.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий данные пользователя и форму изменения пароля.

    Возвращает:
        HttpResponseRedirect: Перенаправляет пользователя на главную страницу после успешного изменения пароля.
        Или страницу с формой изменения пароля в случае ошибок валидации.

    Примечание:
        Если пользователь не аутентифицирован, он будет перенаправлен на страницу входа.
    """
    if not request.user.is_authenticated:
        return redirect('login')

    logger.info(f"Запрос на изменение пароля для пользователя {request.user.username}")
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновляем сессию для пользователя
            messages.success(request, 'Ваш пароль был успешно изменен.')
            logger.info(f"Пароль для пользователя {request.user.username} успешно изменён.")
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
            logger.warning(f"Ошибка при изменении пароля для пользователя {request.user.username}: {form.errors}")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'first/change_password.html', {'form': form})


def table_view(request):
    """
    Отображает таблицу с данными о дебиторах.

    Эта функция получает все данные о дебиторах из базы данных и передает их в шаблон для отображения.
    В журнал записывается информация о доступе к таблице и полученных данных.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Отображает страницу с таблицей дебиторов.
    """
    logger.info("Доступ к просмотру таблицы.")
    # Отображение таблицы с дебиторами
    debtors = Debtor.objects.all()
    logger.info(f"Данные о дебиторах: {debtors}")
    return render(request, 'first/table.html', {'debtors': debtors})


@login_required
def personal_cabinet(request):
    """
    Отображает личный кабинет пользователя с его заявками.

    Эта функция отображает личный кабинет пользователя, где он может видеть свои заявки
    на добавление дебиторов. Доступ к кабинету разрешен только аутентифицированным пользователям.
    В журнал записывается информация о доступе пользователя к его кабинету.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем пользователе.

    Возвращает:
        HttpResponse: Отображает страницу личного кабинета с заявками пользователя.
    """
    logger.info(f"Доступ к личному кабинету пользователя {request.user.username}")
    # Отображение личного кабинета пользователя, где он может видеть свои заявки
    requests = AddDebtorUser.objects.filter(user=request.user)
    return render(request, 'first/personalAccount.html', {'requests': requests})


@login_required
def add_request(request):
    """
    Обрабатывает добавление новой заявки на дебитора.

    Эта функция обрабатывает запросы на добавление новой заявки, заполняя форму
    для создания заявки на дебитора. После успешной отправки формы, заявка сохраняется
    в базе данных и пользователь перенаправляется на страницу личного кабинета.

    Только аутентифицированные пользователи могут добавлять заявки.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета или отображение формы добавления заявки.
    """
    if request.method == 'POST':
        form = DebtorRequestForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохранение новой заявки на дебитора
            debtor_request = form.save(commit=False)
            debtor_request.user = request.user
            debtor_request.save()
            logger.info(f"Заявка на дебитора добавлена пользователем {request.user.username}")
            return redirect('personal_cabinet')
    else:
        form = DebtorRequestForm()
    return render(request, 'add_request.html', {'form': form})


@login_required
def edit_request(request, pk):
    """
    Обрабатывает редактирование существующей заявки на дебитора.

    Эта функция позволяет пользователю редактировать свою заявку на дебитора.
    Если форма успешно отправлена и валидна, изменения сохраняются в базе данных,
    и пользователь перенаправляется в личный кабинет. В случае ошибки форма повторно отображается
    с валидными данными для исправления.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.
        pk (int): Первичный ключ заявки на дебитора, который будет редактироваться.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета, если изменения сохранены,
        или отображение формы редактирования заявки.
    """
    debtor_request = get_object_or_404(AddDebtorUser, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DebtorRequestForm(request.POST, request.FILES, instance=debtor_request)
        if form.is_valid():
            form.save()
            logger.info(f"Заявка на дебитора обновлена пользователем {request.user.username}")
            return redirect('personal_cabinet')
    else:
        form = DebtorRequestForm(instance=debtor_request)
    return render(request, 'edit_request.html', {'form': form})


@login_required
def delete_request(request, pk):
    """
    Обрабатывает удаление заявки на дебитора.

    Эта функция позволяет пользователю удалить свою заявку на дебитора. При подтверждении
    удаления (через POST-запрос) заявка удаляется из базы данных, и пользователь перенаправляется
    в личный кабинет. В случае GET-запроса отображается страница с подтверждением удаления.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.
        pk (int): Первичный ключ заявки на дебитора, которую необходимо удалить.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета после успешного удаления
        или отображение страницы подтверждения удаления.
    """
    debtor_request = get_object_or_404(AddDebtorUser, pk=pk, user=request.user)
    if request.method == 'POST':
        debtor_request.delete()
        logger.info(f"Заявка на дебитора удалена пользователем {request.user.username}")
        return redirect('personal_cabinet')
    return render(request, 'delete_request.html', {'request_obj': debtor_request})


@login_required
def update_telegram(request):
    """
    Обрабатывает обновление Telegram-аккаунта пользователя.

    Эта функция позволяет пользователю обновить свой Telegram-аккаунт в личном кабинете.
    Если предоставлено новое значение для Telegram, оно сохраняется, и пользователю
    показывается сообщение об успешном обновлении. Если поле пустое, выводится ошибка.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета после попытки обновления Telegram.
    """
    if request.method == 'POST':
        telegram = request.POST.get('telegram')
        if telegram:
            request.user.tg_account = telegram
            request.user.save()
            messages.success(request, 'Ваш Telegram успешно обновлен!')
            logger.info(f"Пользователь {request.user.username} обновил свой Telegram.")
        else:
            messages.error(request, 'Поле Telegram не может быть пустым.')
            logger.warning(f"Ошибка при обновлении Telegram для пользователя {request.user.username} - поле пустое.")
        return redirect('personal_cabinet')
    return redirect('personal_cabinet')


@login_required
def update_full_name(request):
    """
    Обрабатывает обновление имени и фамилии пользователя.

    Эта функция позволяет пользователю обновить своё имя и фамилию в личном кабинете.
    Если предоставлены оба значения (имя и фамилия), они сохраняются в базе данных,
    и пользователю показывается сообщение об успешном обновлении. В случае, если одно
    из полей пустое, выводится ошибка.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета после попытки обновления имени и фамилии.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        if name and surname:
            request.user.name = name
            request.user.surname = surname
            request.user.save()
            messages.success(request, 'Ваши Имя и Фамилия успешно обновлены!')
            logger.info(f"Пользователь {request.user.username} обновил Имя и Фамилию.")
        else:
            messages.error(request, 'Поле Имя и Фамилия не может быть пустым.')
            logger.warning(
                f"Ошибка при обновлении Имени и Фамилии для пользователя {request.user.username} - поля пустые.")
        return redirect('personal_cabinet')
    return redirect('personal_cabinet')


@login_required
def update_email(request):
    """
    Обрабатывает обновление email-адреса пользователя.

    Эта функция позволяет пользователю обновить свой email-адрес в личном кабинете.
    Если введённый email уже существует в базе данных, выводится сообщение об ошибке.
    В случае, если email пуст, также выводится ошибка. Если email успешно обновлён,
    пользователю показывается сообщение об успешном обновлении.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета после попытки обновления email.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if NewUsers.objects.filter(email=email).exists():
                messages.error(request, 'Этот Email уже зарегистрирован другим пользователем.')
                logger.warning(
                    f"Ошибка при обновлении Email для пользователя {request.user.username} - email уже используется.")
            else:
                request.user.email = email
                request.user.save()
                messages.success(request, 'Ваш Email успешно обновлен!')
                logger.info(f"Пользователь {request.user.username} обновил свой Email.")
        else:
            messages.error(request, 'Поле Email не может быть пустым.')
            logger.warning(f"Ошибка при обновлении Email для пользователя {request.user.username} - поле пустое.")
        return redirect('personal_cabinet')
    return redirect('personal_cabinet')


@login_required
def add_debtor(request):
    """
    Обрабатывает добавление нового дебитора в систему.

    Эта функция позволяет пользователю добавить нового дебитора, указав обязательные данные, такие как имя,
    фамилию, сумму долга, адрес, регион и город. Также пользователю нужно загрузить документ, подтверждающий
    информацию. Если данные введены неверно (например, сумма долга не может быть преобразована в число),
    выводится сообщение об ошибке. В случае успешного добавления дебитора, показывается сообщение об успехе.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.

    Возвращает:
        HttpResponse: Перенаправление на страницу личного кабинета после попытки добавить дебитора.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        amount = request.POST.get('amount')
        address = request.POST.get('address')
        region = request.POST.get('region')
        city = request.POST.get('city')
        document = request.FILES.get('document')

        # Проверка обязательных полей
        if name and surname and amount and address and region and city:
            try:
                AddDebtorUser.objects.create(
                    name=name,
                    surname=surname,
                    amount=Decimal(amount),  # Преобразование строки в число
                    address=address,
                    region=region,
                    city=city,
                    document=document,
                    user=request.user
                )
                messages.success(request, 'Дебитор успешно добавлен!')
                logger.info(f"Дебитор {name} {surname} добавлен пользователем {request.user.username}.")
            except InvalidOperation:
                messages.error(request, 'Неверно введена сумма!')
                logger.warning(f"Ошибка при добавлении дебитора {name} {surname} - неверная сумма.")
        else:
            messages.error(request, 'Заполнены не все обязательные поля!')
            logger.warning(f"Дебитор {name} {surname} не добавлен - отсутствуют обязательные поля.")

        return redirect('personal_cabinet')
    return redirect('personal_cabinet')


@login_required
def update_debtor(request, debtor_id):
    """
    Обрабатывает обновление информации о дебиторе.

    Эта функция позволяет пользователю обновить данные о дебиторе, такие как имя, фамилия, сумма долга, адрес,
    регион и город. Также пользователь может загрузить новый документ, если это необходимо. Если дебитор с указанным
    ID не найден, выводится сообщение об ошибке. В случае успешного обновления, выводится сообщение об успехе, и
    пользователь перенаправляется в личный кабинет.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий информацию о текущем запросе.
        debtor_id (int): ID дебитора, информацию о котором нужно обновить.

    Возвращает:
        HttpResponse: Перенаправление в личный кабинет пользователя после обновления информации о дебиторе.
    """
    # Обновление информации о дебиторе
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        amount = request.POST.get('amount')
        address = request.POST.get('address')
        region = request.POST.get('region')
        city = request.POST.get('city')
        document = request.FILES.get('document')

        try:
            debtor = AddDebtorUser.objects.get(id=debtor_id, user=request.user)
            debtor.name = name
            debtor.surname = surname
            debtor.amount = amount
            debtor.address = address
            debtor.region = region
            debtor.city = city
            if document:
                debtor.document = document
            debtor.save()

            messages.success(request, 'Информация о дебиторе успешно обновлена!')
            logger.info(
                f"Информация о дебиторе обновлена пользователем {request.user.username} для дебитора {debtor_id}")
            return redirect('personal_cabinet')
        except AddDebtorUser.DoesNotExist:
            messages.error(request, 'Дебитор не найден.')
            logger.error(f"Дебитор с id {debtor_id} не найден для пользователя {request.user.username}.")
            return redirect('personal_cabinet')
    return redirect('personal_cabinet')


@login_required
def edit_debtor(request, debtor_id):
    """
    Обработчик для редактирования данных дебитора.

    Эта функция позволяет пользователю редактировать данные о дебиторе, такие как имя, фамилия, сумма долга, адрес,
    регион, город и описание изменений. Если предоставлены данные, они обновляются в базе данных. Если были изменения
    в сумме, функция пытается преобразовать строковое значение в числовой формат, и если преобразование не удается,
    выводится ошибка. При успешном обновлении дебитор получает статус "update_requested", что означает, что изменения
    ожидают подтверждения. Также пользователь получает уведомление об успешном обновлении.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий данные для обновления.
        debtor_id (int): ID дебитора, данные которого нужно обновить.

    Возвращает:
        HttpResponse: Перенаправление в личный кабинет после успешного обновления или ошибки.
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

        # Логирование начала процесса редактирования
        logger.info(f"Пользователь {request.user.username} начал редактирование дебитора с id {debtor_id}.")

        # Находим дебитора по ID и текущему пользователю
        try:
            debtor = AddDebtorUser.objects.get(id=debtor_id, user=request.user)
            logger.info(f"Дебитор с ID {debtor_id} найден. Начинаем обновление данных.")
        except AddDebtorUser.DoesNotExist:
            messages.error(request, "Дебитор не найден.")
            logger.error(f"Дебитор с ID {debtor_id} не найден для пользователя {request.user.username}.")
            return redirect('personal_cabinet')

        # Обновляем данные, только если они были переданы в запросе
        if name:
            debtor.name = name
            logger.info(f"Имя дебитора изменено на {name}.")
        if surname:
            debtor.surname = surname
            logger.info(f"Фамилия дебитора изменена на {surname}.")

        if amount:
            try:
                # Заменяем запятую на точку, если она есть
                amount = amount.replace(',', '.')
                # Преобразуем строку в Decimal
                debtor.amount = Decimal(amount)
                logger.info(f"Сумма дебитора изменена на {debtor.amount}.")
            except (InvalidOperation, ValueError):
                # Если преобразование не удалось, отправляем ошибку
                messages.error(request, "Неверный формат суммы.")
                logger.error(f"Ошибка преобразования суммы: неверный формат {amount}.")
                return redirect('personal_cabinet')

        if address:
            debtor.address = address
            logger.info(f"Адрес дебитора изменен на {address}.")
        if region:
            debtor.region = region
            logger.info(f"Регион дебитора изменен на {region}.")
        if city:
            debtor.city = city
            logger.info(f"Город дебитора изменен на {city}.")
        if update_description:  # Если описание изменений есть
            debtor.update_description = update_description
            logger.info(f"Добавлено описание изменений: {update_description}.")
        if document:  # Если есть новый документ
            debtor.document = document
            logger.info(f"Загружен новый документ для дебитора.")
        if created_at:
            debtor.created_at = created_at
            logger.info(f"Дата создания дебитора обновлена на {created_at}.")

        # Устанавливаем статус на "На обновление"
        debtor.status = status
        logger.info(f"Статус дебитора обновлен на 'update_requested'.")

        # Сохраняем изменения
        debtor.save()

        # Уведомляем пользователя об успешном обновлении
        messages.success(request, 'Дебитор успешно обновлен! Ожидайте подтверждения от администратора.')
        logger.info(f"Дебитор с ID {debtor_id} успешно обновлен пользователем {request.user.username}.")

        # Перенаправляем после успешного редактирования
        return redirect('personal_cabinet')

    else:
        # Для GET запроса, возвращаем на личный кабинет
        logger.warning(
            f"Пользователь {request.user.username} пытался редактировать дебитора с ID {debtor_id} через GET-запрос.")
        return redirect('personal_cabinet')


@login_required
def request_deletion(request, debtor_id):
    """
    Обработчик для запроса на удаление дебитора.

    Эта функция позволяет пользователю отправить запрос на удаление дебитора. Запрос включает указание причины удаления и
    загрузку документа, если необходимо. После отправки запроса статус дебитора изменяется на "deleting". Если форма прошла
    валидацию, данные сохраняются, и пользователю показывается сообщение об успешной отправке запроса. В случае ошибок
    в процессе обработки или если дебитор не найден, выводятся соответствующие сообщения.

    Аргументы:
        request (HttpRequest): Объект запроса, содержащий данные для отправки запроса на удаление.
        debtor_id (int): ID дебитора, для которого запрашивается удаление.

    Возвращает:
        HttpResponse: Перенаправление в личный кабинет после отправки запроса или ошибки.
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

                # Уведомляем пользователя об успешном запросе на удаление
                messages.success(request, 'Запрос на удаление успешно отправлен!')
                logger.info(
                    f"Пользователь {request.user.username} отправил запрос на удаление дебитора {debtor.name} {debtor.surname}.")
            else:
                # Если форма не прошла валидацию, выводим ошибку
                messages.error(request, 'Ошибка при отправке запроса. Пожалуйста, попробуйте снова.')
                logger.warning(
                    f"Пользователь {request.user.username} не смог отправить запрос на удаление дебитора {debtor.name} {debtor.surname} - ошибка в форме.")

        else:
            # В случае GET-запроса, просто показываем сообщение
            messages.info(request, 'Запрос на удаление дебитора')

    except AddDebtorUser.DoesNotExist:
        messages.error(request, 'Дебитор не найден.')
        logger.error(f"Дебитор с id {debtor_id} не найден для пользователя {request.user.username}.")

    # Перенаправляем обратно на личный кабинет
    return redirect('personal_cabinet')
