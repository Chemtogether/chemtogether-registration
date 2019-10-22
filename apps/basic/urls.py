from django.urls import path, include
from . import views

app_name = 'basic'
urlpatterns = [
    path('', views.index, name='home'),
    path('info/', views.index, name='info'),
]