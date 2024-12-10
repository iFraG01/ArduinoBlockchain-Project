from django.urls import path
from . import views

urlpatterns = [
    path('contract/message/', views.contract_message, name='contract_message'),
]
