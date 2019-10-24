from django.urls import path, include
from . import views

app_name = 'basic'
urlpatterns = [
    path('', views.index, name='home'),
    path('info_fair/', views.info_fair, name='info_fair'),
    path('info_application/', views.info_application, name='info_application'),
    path('info_packages/', views.info_packages, name='info_packages'),
]