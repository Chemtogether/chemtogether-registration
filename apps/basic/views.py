import logging
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib import messages
from dynamic_preferences.registries import global_preferences_registry
from apps.profiles.models import Representative

User = get_user_model()
global_preferences = global_preferences_registry.manager()
logger = logging.getLogger("ct_registration.basic.views")

def index(request):

    context = {
        'title': 'Home'
    }

    if not request.user.is_authenticated:   
        return render(request, 'basic/home_public.html', context=context)

    if request.user.is_authenticated:

        if request.user.is_staffmember():
            return render(request, 'basic/home_staff.html', context=context)

        if request.user.is_company_has_not_applied():
            return render(request, 'basic/home_company_no_application.html', context=context)

        if request.user.is_company_has_applied():
            if not request.user.company.get().staff_user:
                representative = Representative.objects.filter(default_contact=True)[0]
            else:
                representative = request.user.company.get().staff_user
            context['representative'] = representative
            return render(request, 'basic/home_company_with_application.html', context=context)



def info_fair(request):

    context = {
        'title': 'Information'
    }

    return render(request, 'basic/info_fair.html', context=context)



def info_application(request):

    context = {
        'title': 'Information'
    }

    return render(request, 'basic/info_application.html', context=context)



def info_packages(request):

    context = {
        'title': 'Information'
    }

    return render(request, 'basic/info_packages.html', context=context)