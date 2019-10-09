from django.db import models
from apps.profiles.models import Company


class DataForm(models.Model):
    corresponding_user = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "Data forms"

