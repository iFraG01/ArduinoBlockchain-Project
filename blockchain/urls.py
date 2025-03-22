from django.urls import path
from django.shortcuts import redirect
from .views import edit_user, get_access_logs_view, get_user_operations_view, receive_esp32_data, user_management, delete_user, add_user,custom_login, custom_logout

urlpatterns = [
    path("login/", custom_login, name="login"),
    path("receive-data/", receive_esp32_data, name="receive_esp32_data"),
    path('get_access_logs/', get_access_logs_view, name='get_access_logs'),
    path('get_user_operations/', get_user_operations_view, name='get_user_operations'),
    path('users/', user_management, name='user_management'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/edit/', edit_user, name='edit_user'),    
    path("logout/", custom_logout, name="logout"),
]