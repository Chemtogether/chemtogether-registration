import logging
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib import messages
from dynamic_preferences.registries import global_preferences_registry
from django.core.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger("ct_registration.companies.models")






def scramble_uploaded_filename(instance, filename):
    prefix = 'staff_images/'
    extension = filename.split(".")[-1]
    uid = uuid.uuid4()
    return "{}{}.{}".format(prefix, uid, extension)






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
        upload_to = scramble_uploaded_filename,
        default = 'staff_images/default.jpg',
        help_text = _('Your picture shown to companies. At least 200x300px portrait and optimally in 2:3 aspect ratio.'),
    )

    default_contact = models.BooleanField(
        verbose_name = _('default contact'),
        default = False,
        help_text = _('Whether this user is to be the default contact person for new companies.'),
    )

    def delete(self, *args, **kwargs):
        self.staff_user.has_profile = False
        self.staff_user.save()
        return super(Representative, self).delete(*args, **kwargs)

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
        verbose_name = _('company name'),
        max_length = 30,
        help_text = _('Title of your company as it will be shown at the fair and in the fair material. Limited to 30 characters.'),
    )

    day = models.IntegerField(
        verbose_name = _('day of the fair'),
        choices =  (
            (1, _("Tuesday, November 2nd")),
            (2, _("Wednesday, November 3rd")),
        ),
        help_text = _('Day of the fair on which your company will attend.'),
    )

    package = models.IntegerField(
        verbose_name = _('choice of package'),
        choices =  (
            (0, _("Base Package")),
            (1, _("Silver Package")),
            (2, _("Gold Package")),
            (3, _("Platinum Package")),
        ),
        help_text = _('Choice of package for your company.'),
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
        help_text = _('Email address of the person of contact for your company. This address will be used for all mail correspondence.'),
    )

    phone_number = models.CharField(
        verbose_name = _('phone number'),
        max_length = 50,
        help_text = _('Phone number of the person of contact for your company.'),
    )

    language = models.IntegerField(
        verbose_name = _('preferred language'),
        choices =  (
            (0, _("English")),
            (1, _("German")),
        ),
        default = 0,
        help_text = _('Preferred language for any correspondence.'),
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
        verbose_name = _('I accept the terms of service'),
        blank = False,
        help_text = _('You must accept the <a href="https://registration.chemtogether.ethz.ch/static/files/tos.pdf" target="_blank">terms of service</a> to apply. The terms of service are only available in german.'),
    )

    comments = models.TextField(
        verbose_name = _('comments'),
        blank = True,
        help_text = _('Additional comments. Optional.'),
    )

    date_of_first_application = models.DateTimeField(
        verbose_name = _('first application'),
        auto_now_add = True,
        help_text = _('Date when the first application of this company was created.'),
    )

    date_of_last_application = models.DateTimeField(
        verbose_name = _('last application'),
        auto_now_add = True,
        help_text = _('Date when the application of this company was last updated.'),
    )

    date_of_accepted_application = models.DateTimeField(
        verbose_name = _('application accepted'),
        null = True,
        blank = True,
        default = None,
        help_text = _('Date when the application of this company was accepted.'),
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
            logger.error("Company %s attempted to save their registration without accepting the ToS." % self.title)
            return
        return super(Company, self).save(*args, **kwargs)

    def clean(self):
        if not self.accepts_tos:
            raise ValidationError('Please accept the Terms of Service.')

    def delete(self, *args, **kwargs):
        if not self.company_user.demote_to_company_has_not_applied():
            logger.error("Demotion of company %s to company without application failed." % self.title)
        return super(Company, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Companies"

