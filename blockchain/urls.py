from django.urls import path
from . import views
from .views import receive_esp32_data,user_management, delete_user, add_user,custom_login, custom_logout

urlpatterns = [
    path('contract/message/', views.contract_message, name='contract_message'),
    path("receive-data/", views.receive_esp32_data, name="receive_esp32_data"),
     path('users/', user_management, name='user_management'),
    path('users/add/', add_user, name='add_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
     path("login/", custom_login, name="login"),  # URL per la pagina di login
    path("logout/", custom_logout, name="logout"),  # URL per il logout
]