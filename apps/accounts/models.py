import logging
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger("ct_registration.accounts.models")


class UserManager(BaseUserManager):
    """ Custom user manager for user creation. """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """ Custom user class with added custom properties. """

    username = None
    email = models.EmailField(_('email address'), unique=True)

    roles = ( #SPECIFICATION: companies must always have value >= 0 and staff < 0 
            (-3, _("Staff: Admin")),    
            (-2, _("Staff: Moderator")),    
            (-1, _("Staff: Viewer")),
            (0, _("Company: no application")),
            (1, _("Company: has applied")),
            (2, _("Company: accepted"))
        )

    role = models.IntegerField(
        _('user role'),
        choices = roles,
        default = 0,
        help_text = _('Designates what role the user has. DO NOT CHANGE THIS MANUALLY UNLESS YOU KNOW WHAT YOU ARE DOING.'),
    )
    is_active = models.BooleanField(
        _('verified status'),
        default = False,
        help_text = _('Designates whether the user has verified its account.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_company(self):
        """ Returns True if the user corresponds to a company account. """
        return self.role >= 0

    def is_company_has_not_applied(self):
        """ Returns True if the user corresponds to a company account that has an account but has not applied yet. """
        return self.role == 0

    def is_company_has_applied(self):
        """ Returns True if the user corresponds to a company account that has applied. """
        return self.role == 1

    def is_company_is_accepted(self):
        """ Returns True if the user corresponds to a company account that has been accepted. """
        return self.role == 2


    def is_staffmember(self):
        """ Returns True if the user corresponds to a staff account. """
        return self.role < 0

    def is_staffmember_has_profile(self):
        """ Returns True if the user corresponds to a staff account with profile. """
        try:
            return self.is_staffmember() and self.profile.get()
        except:
            return False

    def is_staffmember_is_viewer(self):
        """ Returns True if the user corresponds to a staff account with viewer rights. """
        return self.role == -1

    def is_staffmember_is_moderator(self):
        """ Returns True if the user corresponds to a staff account with moderator rights. """
        return self.role == -2
    
    def is_staffmember_is_admin(self):
        """ Returns True if the user corresponds to a staff account with admin rights. """
        return self.role == -3

    def demote_to_staff_viewer(self):
        """ Changes user status to staff without profile. """
        self.role = -1
        self.save()
        return True

    def promote_to_staff_moderator(self):
        """ Changes user status to staff with profile. """
        if not self.role == -1:
            logger.error("Attempted to promote user %s to staff moderator, but user is %s and not staff viewer." % (self.email, self.role))
            return False
        else:
            self.role = -2
            self.save()
            return True

    def demote_to_company_has_not_applied(self):
        """ Changes user status to company without application. """
        self.role = 0
        self.save()
        return True

    def promote_to_company_has_applied(self):
        """ Changes user status to company with application. """
        if not self.role == 0:
            logger.error("Attempted to promote user %s to company with application, but user is %s and not a company without application." % (self.email, self.role))
            return False
        else:
            self.role = 1
            self.save()
            return True

    def promote_to_accepted_company(self):
        """ Changes user status to accepted company. """
        if not self.role == 1:
            logger.error("Attempted to promote user %s to accepted company, but user is %s and not a company with application." % (self.email, self.role))
            return False
        else:
            self.role = 2
            self.save()
            return True

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email