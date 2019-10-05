import slugify
import logging

import account.forms
import account.views
from . import forms

logger = logging.getLogger("ct_registration.main.views")


class LoginView(account.views.LoginView):

    form_class = account.forms.LoginEmailForm





class SignupView(account.views.SignupView):

    form_class = forms.SignupForm
    identifier_field = 'email'

    def generate_username(self, form):
        logger.info(form)
        username = slugify.slugify(form.cleaned_data.get("email"))
        return username