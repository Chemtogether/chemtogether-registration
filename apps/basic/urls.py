from django.urls import path, include
from . import views

app_name = 'basic'
urlpatterns = [
    path('', views.index, name='home'),
    path('info_application/', views.info_application, name='info_application'),
]