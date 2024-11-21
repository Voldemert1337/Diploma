from django.contrib import admin
from .models import NewUsers, Debtor, AddDebtorUser
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Регистрация моделей в админке
admin.site.register(NewUsers)
admin.site.register(Debtor)

@admin.register(AddDebtorUser)
class AddDebtorUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'amount', 'status', 'document', 'created_at', 'updated_at', 'document_link', 'deletion_reason', 'deletion_document',)
    actions = ['approve_selected', 'reject_selected', 'confirm_deletion', 'approve_update', 'reject_update', 'confirm_update']

    # Действие для одобрения выбранных дебиторов
    def approve_selected(self, request, queryset):
        for debtor in queryset:
            if debtor.status == 'pending':
                try:
                    # Создаем запись в основной базе
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
                    main_debtor.save()  # Сохраняем в основной базе

                    # Обновляем статус в AddDebtorUser
                    debtor.status = 'added'
                    debtor.save()

                    self.message_user(request, f"Дебитор {debtor.name} {debtor.surname} успешно одобрен и добавлен в основную базу.")
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} одобрен и добавлен в основную базу.")
                except ValidationError as e:
                    self.message_user(request, f"Ошибка при добавлении дебитора в основную базу: {e}", level="error")
                    logger.error(f"Ошибка при добавлении дебитора {debtor.name} в основную базу: {e}")
            else:
                self.message_user(request, f"Дебитор {debtor.name} {debtor.surname} не может быть одобрен, так как его статус не 'pending'.", level="warning")
                logger.warning(f"Дебитор {debtor.name} {debtor.surname} не был одобрен, его статус не 'pending'.")

    approve_selected.short_description = "Одобрить выбранных дебиторов"

    # Действие для отклонения выбранных дебиторов
    def reject_selected(self, request, queryset):
        reason = request.POST.get('rejection_reason', None)
        if reason:
            for debtor in queryset:
                if debtor.status == 'pending':
                    debtor.status = 'rejected'
                    debtor.rejection_reason = reason
                    debtor.save()
                    self.message_user(request, "Выбраные дебиторы успешно отклонены с указанной причиной.")
                    logger.info(f"Дебиторы {', '.join([debtor.name for debtor in queryset])} отклонены с причиной: {reason}")
                else:
                    self.message_user(request, "Пожалуйста, укажите причину отклонения.")
                    logger.warning("Причина отклонения не была указана.")
        else:
            self.message_user(request, "Пожалуйста, укажите причину отклонения.")
            logger.warning("Причина отклонения не была указана.")

    reject_selected.short_description = "Отклонить выбранных дебиторов"

    # Отображение ссылки на документ
    def document_link(self, obj):
        if obj.document:
            return f'<a href="{obj.document.url}" download>Скачать документ</a>'
        return 'Нет документа'

    document_link.short_description = 'Ссылка на документ'

    # Действие для подтверждения удаления
    def confirm_deletion(self, request, queryset):
        for debtor in queryset:
            if debtor.status == 'deleting':
                try:
                    # Удаляем из основной базы
                    main_debtor = Debtor.objects.get(user=debtor.user, index_key=debtor.index_key)
                    main_debtor.delete()  # Удаляем основной объект
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} удален из основной базы.")
                except Debtor.DoesNotExist:
                    self.message_user(request,
                                      f"Запись в основной базе для пользователя {debtor.user} ({debtor.name} {debtor.surname}) не найдена.",
                                      level="warning")
                    logger.warning(f"Запись в основной базе для {debtor.name} {debtor.surname} не найдена.")

                # Удаляем из AddDebtorUser
                debtor.delete()
                self.message_user(request,
                                  f"Должник {debtor.name} {debtor.surname} успешно удален из обеих баз.")
                logger.info(f"Дебитор {debtor.name} {debtor.surname} успешно удален из обеих баз.")
            else:
                self.message_user(
                    request,
                    f"Невозможно удалить должника {debtor.name} {debtor.surname}, так как его статус не 'deleting'.",
                    level="error"
                )
                logger.error(f"Дебитор {debtor.name} {debtor.surname} не может быть удален: неверный статус.")

    confirm_deletion.short_description = "Подтвердить удаление"

    # Кнопка для администратора, чтобы утвердить обновление
    def approve_update(self, request, queryset):
        for debtor in queryset:
            if debtor.status == 'approved_for_update':
                try:
                    # Обновляем данные в основной базе
                    main_debtor = Debtor.objects.get(user=debtor.user, index_key=debtor.index_key)
                    main_debtor.name = debtor.name
                    main_debtor.surname = debtor.surname
                    main_debtor.amount = debtor.amount
                    main_debtor.address = debtor.address
                    main_debtor.region = debtor.region
                    main_debtor.city = debtor.city
                    main_debtor.save()  # Сохраняем в основной базе

                    # Если обновление прошло успешно, меняем статус
                    debtor.status = 'updated_in_db'
                    debtor.save()

                    self.message_user(request,
                                      f"Дебитор {debtor.name} {debtor.surname} успешно обновлен в основной базе.")
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} успешно обновлен в основной базе.")
                except Debtor.DoesNotExist:
                    self.message_user(
                        request,
                        f"Запись в основной базе для пользователя {debtor.user} не найдена.",
                        level="warning"
                    )
                    logger.warning(f"Запись в основной базе для {debtor.name} {debtor.surname} не найдена.")
            else:
                self.message_user(
                    request,
                    f"Дебитор {debtor.name} {debtor.surname} не может быть обновлен, так как его статус не 'approved_for_update'.",
                    level="warning"
                )
                logger.warning(f"Дебитор {debtor.name} {debtor.surname} не может быть обновлен: неверный статус.")

    approve_update.short_description = "Подтвердить обновление данных"

    # Кнопка для администратора, чтобы отклонить обновление
    def reject_update(self, request, queryset):
        for debtor in queryset:
            if debtor.status == 'update_requested':
                debtor.status = 'rejected'
                debtor.save()
                self.message_user(request, f"Обновление данных для дебитора {debtor.name} {debtor.surname} отклонено.")
                logger.info(f"Обновление данных для дебитора {debtor.name} {debtor.surname} отклонено.")
            else:
                self.message_user(
                    request,
                    f"Дебитор {debtor.name} {debtor.surname} не может быть отклонен, так как его статус не 'update_requested'.",
                    level="warning"
                )
                logger.warning(f"Дебитор {debtor.name} {debtor.surname} не может быть отклонен: неверный статус.")

    reject_update.short_description = "Отклонить обновление данных"

    # Кнопка для администратора, чтобы подтвердить обновление
    def confirm_update(self, request, queryset):
        for debtor in queryset:
            logger.info(f"Обрабатываем дебитора {debtor.name} {debtor.surname}")
            if debtor.status == 'update_requested':
                try:
                    update_debtor = Debtor.objects.get(user=debtor.user, index_key=debtor.index_key)
                    logger.info(f"Найден дебитор {update_debtor.name} для обновления")

                    # Обновление данных
                    update_debtor.name = debtor.name
                    update_debtor.surname = debtor.surname
                    update_debtor.amount = debtor.amount
                    update_debtor.address = debtor.address
                    update_debtor.region = debtor.region
                    update_debtor.city = debtor.city
                    update_debtor.save()

                    debtor.status = 'updated_in_db'
                    debtor.save()

                    self.message_user(request,
                                      f"Дебитор {debtor.name} {debtor.surname} успешно обновлен в основной базе.")
                    logger.info(f"Дебитор {debtor.name} {debtor.surname} успешно обновлен в основной базе.")
                except Debtor.DoesNotExist:
                    self.message_user(request,
                                      f"Запись в основной базе для пользователя {debtor.user} с index_key {debtor.index_key} не найдена.",
                                      level="warning")
                    logger.warning(f"Дебитор с index_key {debtor.index_key} не найден.")
            else:
                self.message_user(request,
                                  f"Невозможно подтвердить обновление для дебитора {debtor.name} {debtor.surname}, так как его статус не 'update_requested'.",
                                  level="warning")
                logger.warning(f"Невозможно обновить дебитора {debtor.name} {debtor.surname}: неверный статус.")

class NewUsersAdmin(UserAdmin):
    model = NewUsers
    list_display = ('username', 'name', 'surname', 'email', 'is_staff', 'is_active', 'age', 'subscription')
    search_fields = ('username', 'email', 'name', 'surname')
    ordering = ('username',)
