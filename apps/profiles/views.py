import logging

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.contrib import messages


from .forms import ApplicationForm, RepresentativeForm

logger = logging.getLogger("ct_registration.profiles.views")


def FairApplication(request):

    if not request.user.is_authenticated:   
        return HttpResponseRedirect('/')

    else:
        if request.user.is_company_has_not_applied():
            return FairApplication_Form(request)    
        elif request.user.is_company_has_applied():
            try:
                return FairApplication_Form(request, existing_profile = request.user.company.get())
            except Exception as e:
                logger.exception("No existing profile found even tough it should be present.")
                messages.add_message(request, messages.ERROR, 'An error occurred, please submit the form again or contact us via mail.')
                return FairApplication_Form(request)
        else:
            return HttpResponseRedirect('/')


def FairApplication_Form(request, existing_profile = None):

    # if a POST request
    if request.method == 'POST':

        if existing_profile is not None:
            form = ApplicationForm(request.POST, instance = existing_profile)
        else:
            form = ApplicationForm(request.POST)


        if form.is_valid():
            
            company = form.save(commit=False)
            company.company_user = request.user
            if existing_profile is None: 
                if not company.company_user.promote_to_company_has_applied():
                    messages.add_message(request, messages.ERROR, 'An error occurred, please contact us via mail.')
                    return redirect('profiles:application')
                else:
                    messages.add_message(request, messages.INFO, 'Your application was successfully submitted. Note that your application is not a fixed registration to the event. Your registration is only valid after confirmation and explicit acceptance of your application in written form by us.')
                    company.save()
                    return redirect('basic:home')
            else:
                    messages.add_message(request, messages.INFO, 'Your application was successfully updated.')
                    company.save()
                    return redirect('profiles:application')

        else:
            logger.error(form.errors)


    # if a GET request
    else:

        if existing_profile is not None:
            initial_data = model_to_dict(existing_profile, exclude=['accepts_tos'])
            form = ApplicationForm(initial = initial_data)
        else:
            form = ApplicationForm()

    return render(request, 'profiles/company_application.html', {'form': form})









def RepresentativeSettings(request):

    if not request.user.is_authenticated:   
        return HttpResponseRedirect('/')

    else:

        if request.user.is_staffmember_has_no_profile():
            return RepresentativeSettings_Form(request)
        
        elif request.user.is_staffmember_has_profile() or request.user.is_staffmember_is_admin():
            try:
                return RepresentativeSettings_Form(request, existing_profile = request.user.profile.get())
            except Exception as e:
                logger.exception("No existing profile found even tough it should be present.")
                messages.add_message(request, messages.ERROR, 'An error occurred, please submit the form again or contact us via mail.')
                return RepresentativeSettings_Form(request)

        else:
            return HttpResponseRedirect('/')





def RepresentativeSettings_Form(request, existing_profile = None):

    # if a POST request
    if request.method == 'POST':

        if existing_profile is not None:
            form = RepresentativeForm(request.POST, request.FILES, instance = existing_profile)
        else:
            form = RepresentativeForm(request.POST, request.FILES)


        if form.is_valid():
            
            representative = form.save(commit=False)
            representative.staff_user = request.user
            if existing_profile is None: 
                if not representative.staff_user.promote_to_staff_with_profile():
                    messages.add_message(request, messages.ERROR, 'An error occurred, please contact us via mail.')
                    return redirect('profiles:representative')
                else:
                    messages.add_message(request, messages.INFO, 'Profile successfully created.')
                    representative.save()
                    return redirect('profiles:representative')
            else:
                    messages.add_message(request, messages.INFO, 'Profile successfully updated.')
                    representative.save()
                    return redirect('profiles:representative')

        else:
            logger.error(form.errors)

    # if a GET request
    else:

        if existing_profile is not None:
            initial_data = model_to_dict(existing_profile, exclude=[])
            form = RepresentativeForm(initial = initial_data)
        else:
            form = RepresentativeForm()

    return render(request, 'profiles/representative_form.html', {'form': form})


