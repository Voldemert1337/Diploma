from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('get_debtors/', views.get_debtors, name='get_debtors'),
    path('table/', views.table_view, name='table'),
    path('register/', views.user_register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('cabinet/', views.personal_cabinet, name='personal_cabinet'),
    path('add/', views.add_request, name='add_request'),
    path('edit/<int:pk>/', views.edit_request, name='edit_request'),
    path('delete/<int:pk>/', views.delete_request, name='delete_request'),
    path('update-telegram/', views.update_telegram, name='update_telegram'),
    path('update_full_name', views.update_full_name, name='update_full_name'),
    path('update_email', views.update_email, name='update_email'),
    path('add-debtor/', views.add_debtor, name='add_debtor'),
    path('edit-debtor/<int:debtor_id>/', views.edit_debtor, name='edit_debtor'),
    path('delete-debtor/<int:debtor_id>/', views.delete_debtor, name='delete_debtor')
]
