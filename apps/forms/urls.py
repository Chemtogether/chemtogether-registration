from django.urls import re_path

from .views import FormDetail

app_name = 'forms'
urlpatterns = [
    re_path(r"(?P<slug>.*)/$", FormDetail.as_view(), name="form_detail"),
]
