from django.urls import path, include, re_path
from . import views

app_name = 'profiles'
urlpatterns = [
    path('company_application/', views.FairApplication, name='application'),
    path('representative_form/', views.RepresentativeSettings, name='representative'),
    path('user_list/', views.UserList, name='userlist'),
    path('company_list/', views.CompanyList, name='companylist'),
    re_path(r'^staff_detail/(?P<id>\d+)/$', views.StaffDetail, name='staffdetail'), 
    re_path(r'^company_detail/(?P<id>\d+)/$', views.CompanyDetail, name='companydetail'), 
    path('company_detail_assign_staff/', views.CompanyDetail_AssignStaffForm, name='assignstaff'),
    path('company_detail_accept_company/', views.CompanyDetail_AcceptCompanyForm, name='acceptcompany'),
]