import logging
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import messages
from dynamic_preferences.registries import global_preferences_registry

User = get_user_model()
logger = logging.getLogger("ct_registration.companies.models")



class Representative(models.Model):
    """ Model for a representative being the person of contact for a company, summarizing contact information. """

    staff_user = models.ForeignKey(
        User, 
        verbose_name = _('staff account'),
        on_delete = models.SET_NULL, 
        limit_choices_to = {'role__lt': 0},
        related_name = 'profile',
        null = True,
        help_text = _('The user account this profile is linked to.'),
    )

    first_name = models.CharField(
        verbose_name = _('first name'),
        max_length = 50,
        help_text = _('First name.'),
    )

    last_name = models.CharField(
        verbose_name = _('last name'),
        max_length = 50,
        help_text = _('Surname.'),
    )

    email = models.EmailField(
        verbose_name = _('mail address'),
        help_text = _('Email address for communication with companies.'),
    )

    phone_number = models.CharField(
        verbose_name = _('phone number'),
        max_length = 50,
        help_text = _('Phone number for communication with companies.'),
    )

    image = models.ImageField(
        verbose_name = _('picture'),
        upload_to = 'staff_images/',
        default = 'staff_images/default.jpg',
        help_text = _('Your picture shown to companies.'),
    )

    def __str__(self):
        return self.first_name + " " + self.last_name




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

    title = models.CharField(
        verbose_name = _('first name'),
        max_length = 30,
        help_text = _('Title of the company as it will be shown at the fair and in the fair material. Limited to 30 characters.'),
    )

    day = models.IntegerField(
        verbose_name = _('day of the fair'),
        choices =  (
            (1, _("Tuesday")),
            (2, _("Wednesday")),
        ),
        help_text = _('Day of the fair on which this company will attend.'),
    )

    package = models.IntegerField(
        verbose_name = _('choice of package'),
        choices =  (
            (0, _("Base Package")),
            (1, _("Silver Package")),
            (2, _("Gold Package")),
            (3, _("Platinum Package")),
        ),
        help_text = _('Choice of package for this company.'),
    )

    first_name = models.CharField(
        verbose_name = _('first name'),
        max_length = 50,
        help_text = _('First name of the person of contact for your company.'),
    )

    last_name = models.CharField(
        verbose_name = _('last name'),
        max_length = 50,
        help_text = _('Surname of the person of contact for your company.'),
    )

    email = models.EmailField(
        verbose_name = _('mail address'),
        help_text = _('Email addressof the person of contact for your company.'),
    )

    phone_number = models.CharField(
        verbose_name = _('phone number'),
        max_length = 50,
        help_text = _('Phone number of the person of contact for your company.'),
    )

    mailing_address = models.TextField(
        verbose_name = _('mailing address'),
        help_text = _('Address used for mailings.'),
    )

    billing_address = models.TextField(
        verbose_name = _('billing address'),
        help_text = _('Address used for billing.'),
    )

    accepts_tos = models.BooleanField(
        verbose_name = _('accept terms of service'),
        help_text = _('You must accept the terms of service to apply.'),
    )

    comments = models.TextField(
        verbose_name = _('comments'),
        null = True,
        help_text = _('Additional comments. Optional.'),
    )

    staff_user = models.ForeignKey(
        Representative, 
        verbose_name = _('staff account'),
        on_delete = models.SET_NULL, 
        related_name = 'companies',
        null = True,
        help_text = _('Person of contact for this company.'),
    )

    def save(self, *args, **kwargs):
        if not self.accepts_tos:
            logger.error("Company %s attempted to save their registration without accepting the TOS." % self.title)
            return
        if not self.company_user.promote_to_registered_company():
            logger.error("Promotion of company %s to registered company failed." % self.title)
            return
        return super(Company, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.company_user.demote_to_nonregistered_company():
            logger.error("Demotion of company %s to non-registered company failed." % self.title)
        return super(Company, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Companies"

