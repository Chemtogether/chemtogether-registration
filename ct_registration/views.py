import re
import logging

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.contrib import messages
from dynamic_preferences.registries import global_preferences_registry

User = get_user_model()
global_preferences = global_preferences_registry.manager()
logger = logging.getLogger("ct_registration.main.views")


def signup(request):
    """ Renders the signup form, processes its POST data to create inactive users and send verification emails. """
    # check if registration is open
    if global_preferences['account_creation__account_creation_open']:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                email = form.cleaned_data.get('email')

                # user is not yet verified, so make it inactive
                user.is_active = False

                # automatic staff account creation based on email domain
                try:
                    if global_preferences['account_creation__staff_account_domain_enabled'] and re.search("@.+", email).group(0) == '@' + global_preferences['account_creation__staff_account_domain']:
                        prefix = re.search("^.+@", email).group(0)[0:-1]
                        if not global_preferences['account_creation__staff_account_whitelist'] or prefix in global_preferences['account_creation__staff_account_whitelist'].split(','):
                            user.role = -1
                            logger.info("Recognized email %s as staff account." % email)
                except:
                    messages.add_message(request, messages.WARNING, 'You are not whitelisted for a staff account, or there was an error.')
                    logger.error("User %s failed due to not being whitelisted or there was an error." % email)
                    

                # save user and send verification email
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Verify your account'
                message = render_to_string('registration/signup_email.html', {
                    'user': user,
                    'protocol': request.scheme,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                email = EmailMessage(
                            mail_subject, message, to=[email]
                )
                email.send()

                # show signup confirmation page
                return render(request, 'registration/signup_confirm.html')
        else:
            form = SignupForm()
        return render(request, 'registration/signup.html', {'form': form})
    else:
        return render(request, 'registration/signup_closed.html')



def activate(request, uidb64, token):
    """ Allows the user to proceed to account verification with confirm. """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.error("Activation of unknown user requested.")
        user = None

    if user is not None:
        logger.info("Verification of user %s can proceed." % user)
        return render(request, 'registration/signup_forward_to_activation.html', {'uidb64': uidb64, 'token': token})
    else:
        logger.error("Attempt to forward to verification of user %s failed because user is none" % user)
        return render(request, 'registration/signup_invalid.html')


def confirm(request, uidb64, token):
    """ Uses the token in the url send to the user to verify user email. """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        logger.error("Activation of unknown user requested.")
        user = None


    if user is not None and user.is_active:
        # user is already verified, forward to login
        logger.info("Verification of user %s skipped because it was already verified." % user)
        messages.add_message(request, messages.INFO, 'Your account is verified. Please log in.')
        return redirect('/login')

    if user is not None and account_activation_token.check_token(user, token):
        # url token was valid, activate user and log in
        user.is_active = True
        user.save()
        #login(request, user)
        logger.info("Verification of user %s succeeded." % user)
        messages.add_message(request, messages.INFO, 'Your account was successfully verified. You may log in now.')
        return redirect('/login')

    if user is None:
        logger.error("Verification of user %s failed because user is none" % user)
        return render(request, 'registration/signup_invalid.html')
    else:
        logger.error("Verification of inactive user %s failed because token check failed" % user)
        messages.add_message(request, messages.INFO, 'Your account is verified. Please log in.')
        return redirect('/login')