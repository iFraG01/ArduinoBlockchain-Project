from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('blockchain/', include('blockchain.urls')),
    path('admin/', admin.site.urls),
]
