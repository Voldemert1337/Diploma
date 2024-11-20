import random
from django.core.management.base import BaseCommand
from faker import Faker
from Task1.models import Debtor, NewUsers

class Command(BaseCommand):
    help = 'Генерирует 50 случайных должников для базы данных'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')  # Используем русскую локализацию для Faker

        # Получаем всех пользователей (можно заменить на конкретных пользователей, если нужно)
        users = NewUsers.objects.all()

        regions = ['Московская область', 'Ленинградская область', 'Татарстан', 'Краснодарский край', 'Кемеровская область']
        cities = ['Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск', 'Краснодар']

        # Генерация 50 должников
        for _ in range(100):
            # Выбираем случайного пользователя
            user = random.choice(users)

            # Генерация случайных данных для должника
            debtor = Debtor(
                user=user,
                name=fake.first_name(),
                surname=fake.last_name(),
                amount=round(random.uniform(1000, 100000), 2),  # Генерируем случайную сумму долга от 1000 до 100000
                address=fake.address(),
                region=random.choice(regions),
                city=random.choice(cities),
                created_at=fake.date_this_decade(),
                updated_at=fake.date_this_year()
            )
            debtor.save()

        self.stdout.write(self.style.SUCCESS('Успешно созданы 50 случайных должников'))
