from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
import logging

from .models import NewUsers, Debtor, AddDebtorUser

# Настройка логирования
logger = logging.getLogger(__name__)

# Регистрация моделей в админке
admin.site.register(NewUsers)
admin.site.register(Debtor)


@admin.register(AddDebtorUser)
class AddDebtorUserAdmin(admin.ModelAdmin):
    """
    Класс администратора для модели AddDebtorUser.

    Обрабатывает отображение полей в административной панели и доступные действия
    для записи дебитора: одобрение, отклонение, подтверждение обновлений и удаления.

    Атрибуты:
        list_display (tuple): Список полей, которые отображаются в административной панели.
        actions (list): Список доступных действий, которые могут быть применены к выбранным записям.
    """
    list_display = (
        'name', 'surname', 'amount', 'status', 'document', 'created_at',
        'updated_at', 'document_link', 'deletion_reason', 'deletion_document',
    )
    actions = [
        'approve_selected', 'reject_selected', 'confirm_deletion',
        'approve_update', 'reject_update', 'confirm_update',
    ]

    def approve_selected(self, request, queryset):
        """
        Одобрение выбранных дебиторов и добавление их в основную базу данных.

        Для каждого выбранного дебитора проверяется его статус. Если статус 'pending',
        дебитор добавляется в основную базу данных и статус меняется на 'approved' и 'added'.
        В случае ошибки при добавлении дебитора в базу данных, выводится сообщение об ошибке.

        Аргументы:
            request (HttpRequest): Запрос, поступивший от администратора.
            queryset (QuerySet): Список выбранных записей дебиторов.

        Сообщения:
            Выводится сообщение об успешном добавлении дебитора в базу данных или
            об ошибке, если что-то пошло не так.

        Логирование:
            Ведется логирование успешных действий и ошибок, связанных с добавлением
            дебиторов в основную базу.
        """
        for debtor in queryset:
            if debtor.status == 'pending':
                try:
                    main_debtor = Debtor(
                        user=debtor.user,
                        name=debtor.name,
                        surname=debtor.surname,
                        amount=debtor.amount,
                        address=debtor.address,
                        region=debtor.region,
                        city=debtor.city,
                        updated_at=debtor.updated_at,
                        index_key=debtor.index_key,
                    )
                    debtor.status = 'approved'
                    main_debtor.save()

                    debtor.status = 'added'
                    debtor.save()

                    self.message_user(
                        request,
                        f"Дебитор {debtor.name} {debtor.surname} успешно одобрен и добавлен в основную базу."
                    )
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} одобрен и добавлен в основную базу.")
                except ValidationError as e:
                    self.message_user(
                        request,
                        f"Ошибка при добавлении дебитора в основную базу: {e}",
                        level="error"
                    )
                    logger.error(f"Ошибка при добавлении дебитора {debtor.name} в основную базу: {e}")
            else:
                self.message_user(
                    request,
                    f"Дебитор {debtor.name} {debtor.surname} не может быть одобрен, так как его статус не 'pending'.",
                    level="warning"
                )
                logger.warning(
                    f"Дебитор {debtor.name} {debtor.surname} не был одобрен, его статус не 'pending'."
                )

    approve_selected.short_description = "Одобрить выбранных дебиторов"

    def reject_selected(self, request, queryset):
        """
        Отклонение выбранных дебиторов с указанием причины отклонения.

        Этот метод обрабатывает отклонение дебиторов с помощью административного интерфейса.
        Для каждого дебитора со статусом 'pending' обновляется статус на 'rejected',
        и сохраняется указанная причина отклонения. Если причина отклонения не указана,
        выводится предупреждающее сообщение.

        Аргументы:
            request (HttpRequest): Запрос, поступивший от администратора.
            queryset (QuerySet): Список выбранных записей дебиторов.

        Сообщения:
            Выводится сообщение об успешном отклонении дебиторов или предупреждение,
            если причина отклонения не была указана.

        Логирование:
            Ведется логирование отклоненных дебиторов с указанием причины отклонения
            и предупреждения, если причина не была указана.
        """
        reason = request.POST.get('rejection_reason', None)
        if reason:
            for debtor in queryset:
                if debtor.status == 'pending':
                    debtor.status = 'rejected'
                    debtor.rejection_reason = reason
                    debtor.save()
                    self.message_user(
                        request,
                        "Выбраные дебиторы успешно отклонены с указанной причиной."
                    )
                    logger.info(
                        f"Дебиторы {', '.join([debtor.name for debtor in queryset])} отклонены с причиной: {reason}"
                    )
        else:
            self.message_user(request, "Пожалуйста, укажите причину отклонения.")
            logger.warning("Причина отклонения не была указана.")

    reject_selected.short_description = "Отклонить выбранных дебиторов"

    def document_link(self, obj):
        """
        Генерирует ссылку для скачивания документа дебитора.

        Этот метод проверяет наличие документа у дебитора. Если документ существует,
        создается ссылка для его скачивания. Если документа нет, выводится сообщение "Нет документа".

        Аргументы:
            obj (AddDebtorUser): Экземпляр модели AddDebtorUser, для которого проверяется наличие документа.

        Возвращает:
            str: HTML-ссылка для скачивания документа, если он существует, или сообщение "Нет документа".
        """
        if obj.document:
            return f'<a href="{obj.document.url}" download>Скачать документ</a>'
        return 'Нет документа'

    document_link.short_description = 'Ссылка на документ'

    def confirm_deletion(self, request, queryset):
        """
        Подтверждает удаление выбранных дебиторов из основной базы и базы заявок.

        Этот метод обрабатывает удаление дебиторов с состоянием 'deleting'.
        Для каждого такого дебитора из базы данных удаляется связанная запись в основной базе,
        а сам дебитор удаляется из базы заявок. Если запись не найдена в основной базе, выводится предупреждение.

        Аргументы:
            request (HttpRequest): Запрос, поступивший от администратора.
            queryset (QuerySet): Список выбранных дебиторов, которых нужно удалить.

        Сообщения:
            Выводится сообщение об успешном удалении дебитора из обеих баз или предупреждение/ошибка,
            если запись не найдена в основной базе или если статус дебитора не 'deleting'.

        Логирование:
            Ведется логирование успешного удаления дебитора и случаев, когда запись не была найдена,
            или статус дебитора неверен.
        """
        for debtor in queryset:
            if debtor.status == 'deleting':
                try:
                    main_debtor = Debtor.objects.get(
                        user=debtor.user,
                        index_key=debtor.index_key
                    )
                    main_debtor.delete()
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} удален из основной базы.")
                except Debtor.DoesNotExist:
                    self.message_user(
                        request,
                        f"Запись в основной базе для пользователя {debtor.user} "
                        f"({debtor.name} {debtor.surname}) не найдена.",
                        level="warning"
                    )
                    logger.warning(f"Запись в основной базе для {debtor.name} {debtor.surname} не найдена.")

                debtor.delete()
                self.message_user(
                    request,
                    f"Должник {debtor.name} {debtor.surname} успешно удален из обеих баз."
                )
                logger.info(f"Дебитор {debtor.name} {debtor.surname} успешно удален из обеих баз.")
            else:
                self.message_user(
                    request,
                    f"Невозможно удалить должника {debtor.name} {debtor.surname}, так как его статус не 'deleting'.",
                    level="error"
                )
                logger.error(f"Дебитор {debtor.name} {debtor.surname} не может быть удален: неверный статус.")

    confirm_deletion.short_description = "Подтвердить удаление"


class NewUsersAdmin(UserAdmin):
    """
    Административная модель для управления пользователями NewUsers.

    Этот класс настраивает отображение и функциональность административного интерфейса для модели NewUsers.
    Включает отображение полей, настройки поиска и сортировки, а также управление правами пользователей.

    Атрибуты:
        model (Model): Модель, с которой работает данный класс (NewUsers).
        list_display (tuple): Список полей, которые отображаются в списке объектов модели.
        search_fields (tuple): Список полей, по которым можно искать в административном интерфейсе.
        ordering (tuple): Поля для сортировки списка объектов.
    """
    model = NewUsers

    # Список полей для отображения в административном интерфейсе
    list_display = (
        'username', 'name', 'surname', 'email',
        'is_staff', 'is_active', 'age', 'subscription',
    )

    # Настройки поиска по полям в административном интерфейсе
    search_fields = ('username', 'email', 'name', 'surname')

    # Сортировка по умолчанию
    ordering = ('username',)
