# **Дебитор-трекер** - Дипломный проект

## **Описание проекта**

Дебитор-трекер — это веб-приложение для управления данными о дебиторах. Проект позволяет пользователям добавлять, редактировать и отслеживать задолженности. Также предусмотрена система авторизации для пользователей, которые могут работать только с собственными данными.

## **Основные особенности:**

- **Регистрация и авторизация** пользователей.
- Возможность добавления, редактирования и удаления данных о дебиторах.
- История изменений и статусы заявок.
- Простой и удобный интерфейс на основе **Bootstrap** и **DataTables**.
- Логирование ошибок и событий для удобства отладки и мониторинга.

## **Технологии:**

- **Django** 5.1.3
- **Django REST Framework** 3.15.2
- **SQLite** (по умолчанию, можно настроить другие СУБД)
- **Bootstrap** 5.3 для стилизации
- **DataTables** для работы с таблицами
- **Python 3.x**

## **Зависимости**

Для работы проекта требуется установить следующие зависимости:

- asgiref==3.8.1
- Django==5.1.3
- django-timezone-field==7.0
- djangorestframework==3.15.2
- Faker==33.0.0
- python-dateutil==2.9.0.post0
- six==1.16.0
- sqlparse==0.5.2
- typing_extensions==4.12.2
- tzdata==2024.2




## **Установка и запуск проекта**

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Voldemert1337/Diploma.git
cd Дипломный-проект
```

### 2. Создайте виртуальное окружение и активируйте его

```bash
python -m venv myenv
source myenv/bin/activate   # для Linux/MacOS
myenv\Scripts\activate      # для Windows
```
### 3. Установите зависимости

```bash
pip install -r requirements.txt
```
###  4. Примените миграции базы данных

```bash
python manage.py migrate
```

### 5. Создайте суперпользователя для доступа к админ-панели

```bash
python manage.py createsuperuser
```

### 6. Запустите сервер

```bash
python manage.py runserver
```

Теперь проект доступен по адресу: http://127.0.0.1:8000/.

## Скриншоты
### Главная страница
![main_page.png](screenshots/main_page.png)

### Страница базы данных
![database_page.png](screenshots/database_page.png)

### Страница регистрации
![registration_page.png](screenshots/registration_page.png)

### Страница входа
![login_page.png](screenshots/login_page.png)

### Личный кабинет пользователя
![personal_cabinet.png](screenshots/personal_cabinet.png)

### Добавление дебитора
![add_debtor_page.png](screenshots/add_debtor_page.png)

### Редактирование дебитора
![edit_debtor_page.png](screenshots/edit_debtor_page.png)

### Страница смены пароля
![change_password_page.png](screenshots/change_password_page.png)

## Структура проекта

```
.idea/                             # Конфигурационные файлы для IDE (например, PyCharm)
Task1/                              # Дополнительные или тестовые файлы, если есть
__pycache__/                        # Кэшированные файлы Python
management/                         # Папка для кастомных команд Django
  └── commands/                     # Дополнительные команды для администрирования
  └── __init__.py                   # Инициализация пакета
migrations/                         # Миграции базы данных Django
models.py                           # Модели базы данных
views.py                            # Представления (views)
debitor_tracker/                    # Основное приложение
  └── __pycache__/                  # Кэшированные файлы Python
  └── __init__.py                   # Инициализация пакета
  └── asgi.py                       # Конфигурация ASGI
  └── settings.py                   # Настройки проекта
  └── urls.py                       # URL маршруты
  └── wsgi.py                       # Конфигурация WSGI
static/                             # Статические файлы (CSS, JS)
  └── bootstrap/                    # Файлы Bootstrap
  └── datatables/                   # Скрипты для DataTables
templates/                          # HTML шаблоны
  └── first/                        # Дополнительные или старые шаблоны
  └── change_password.html          # Шаблон для смены пароля
  └── index.html                    # Главная страница
  └── login.html                    # Страница входа
  └── menu.html                     # Меню пользователя
  └── personalAccount.html          # Личный кабинет
  └── register.html                 # Страница регистрации
  └── table.html                    # Страница с таблицей дебиторов
documents/                          # Папка для хранения документов
  └── backups.txt                   # Резервные копии базы данных
  └── backups_9SbkiKm.txt           # Резервная копия с уникальным именем
db.sqlite3                          # База данных SQLite
debug.log                           # Лог файл ошибок
manage.py                           # Основной файл управления проектом
requirements.txt                    # Список зависимостей
README.md                           # Этот файл
```

## Использование

1. Перейдите в личный кабинет для добавления новых дебиторов.
2. Можете редактировать данные дебиторов и отслеживать изменения.
3. Для администратора доступна админ-панель для управления данными.

## Логирование

Логирование осуществляется через стандартные механизмы Django. Все ошибки записываются в файл debug.log


## Лицензия

Этот проект защищен авторским правом и распространяется на условиях лицензии "All Rights Reserved". Полные условия лицензионного соглашения можно найти в файле [LICENSE](./LICENSE).

## Пользовательское соглашение

Использование проекта регулируется [Пользовательским соглашением](./USER_AGREEMENT.md).


