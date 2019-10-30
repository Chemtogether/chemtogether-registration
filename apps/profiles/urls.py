from django.urls import path, include
from . import views

app_name = 'profiles'
urlpatterns = [
    path('company_application/', views.FairApplication, name='application'),
    path('representative_form/', views.RepresentativeSettings, name='representative'),
]