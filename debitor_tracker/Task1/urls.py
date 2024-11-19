from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('get_debtors/', views.get_debtors, name='get_debtors'),
    path('table/', views.table_view, name='table'),
    path('register/', views.user_register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change_password/', views.change_password, name='change_password')
]
