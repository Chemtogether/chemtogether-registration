import logging
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib import messages
from dynamic_preferences.registries import global_preferences_registry
from apps.profiles.models import Representative
from apps.forms.models import Form, FormEntry, STATUS_PUBLISHED, STATUS_DRAFT

User = get_user_model()
global_preferences = global_preferences_registry.manager()
logger = logging.getLogger("ct_registration.basic.views")

def index(request):

    context = {
        'title': 'Home'
    }
    
    return render(request, 'basic/home_deactivated.html', context=context)
    
    # STOP HERE! Deactivating website to switch to new tool.

    if not request.user.is_authenticated:   
        return render(request, 'basic/home_public.html', context=context)

    if request.user.is_authenticated:

        if request.user.is_staffmember():
            return render(request, 'basic/home_staff.html', context=context)

        if request.user.is_company_has_not_applied():
            return render(request, 'basic/home_company_no_application.html', context=context)

        # get the representative
        if not request.user.company.get().staff_user:
            try:
                representative = Representative.objects.filter(default_contact=True)[0]
            except:
                representative = False
        else:
            representative = request.user.company.get().staff_user
        context['representative'] = representative

        if request.user.is_company_has_applied():
            return render(request, 'basic/home_company_with_application.html', context=context)
        
        if request.user.is_company_is_accepted():
            forms_to_fill_out = Form.objects.published().order_by("-publish_date", "-expiry_date", "title")
            forms_status = []
            for form in forms_to_fill_out:
                try:
                    entry = FormEntry.objects.filter(author=request.user.company.get()).filter(form=form).get()
                    if entry.status == STATUS_DRAFT:
                        forms_status.append('draft')
                    else:
                        forms_status.append('submitted')
                except:
                    forms_status.append(None)

            context['to_dos'] = [{'form': forms_to_fill_out[i], 'status': forms_status[i]} for i in range(0,len(forms_to_fill_out))]
            return render(request, 'basic/home_company_accepted.html', context=context)



def info_application(request):

    context = {
        'title': 'Information'
    }

    return render(request, 'basic/info_application.html', context=context)
