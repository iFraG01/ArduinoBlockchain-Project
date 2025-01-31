from django.urls import path
from . import views
from .views import receive_esp32_data

urlpatterns = [
    path('contract/message/', views.contract_message, name='contract_message'),
    path("receive-data/", views.receive_esp32_data, name="receive_esp32_data"),
]