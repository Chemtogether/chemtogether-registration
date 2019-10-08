from django.db import models
from apps.companies.models import Company


class DataForms(models.Model):
    corresponding_user = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)