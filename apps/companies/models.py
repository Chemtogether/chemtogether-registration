import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


User = get_user_model()
logger = logging.getLogger("ct_registration.companies.models")


class Company(models.Model):
    """ Model for a company which summarizes information collected in the registration process as well as in any further forms. """

    company_user = models.ForeignKey(
        User, 
        verbose_name = _('company account'),
        on_delete = models.SET_NULL, 
        limit_choices_to = {'role__gte': 0},
        related_name = 'company',
        null = True,
        help_text = _('The user account this company is linked to.'),
    )

    staff_user = models.ForeignKey(
        User, 
        verbose_name = _('staff account'),
        on_delete = models.SET_NULL, 
        limit_choices_to = {'role__lt': 0},
        related_name = 'companies',
        null = True,
        help_text = _('Person of contact for this company.'),
    )
