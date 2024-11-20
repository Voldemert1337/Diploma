import os
import django

# Установите переменную окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "debitor_tracker.settings")

# Инициализируйте Django
django.setup()

# Теперь можно импортировать модели
from Task1.models import Region, City

# Очистка базы данных
City.objects.all().delete()
Region.objects.all().delete()

# Ваш код для работы с моделями здесь
import csv

with open('D:/Project/DebtorTracker/debitor_tracker/Task1/cities.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        region_name = row['region']
        city_name = row['city']
        # Получаем или создаем регион
        region, created = Region.objects.get_or_create(name=region_name)
        if created:
            print(f"Добавлен новый регион: {region_name}")
        # Получаем или создаем город, связанный с регионом
        city, created = City.objects.get_or_create(name=city_name, region=region)
        if created:
            print(f"Добавлен новый город: {city_name} в регионе {region_name}")

print("Все города и регионы успешно добавлены в базу данных и связаны правильно!")
