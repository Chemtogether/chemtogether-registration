import logging

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.contrib import messages


from .forms import ApplicationForm, RepresentativeForm, AssignStaffForm, AcceptCompanyForm
from apps.accounts.models import User
from .models import Company, Representative

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
                messages.add_message(request, messages.WARNING, 'An error occurred, please submit the form again or contact us via mail.')
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
                    messages.add_message(request, messages.WARNING, 'An error occurred, please contact us via mail.')
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

        if not request.user.is_staffmember_has_profile():
            return RepresentativeSettings_Form(request)
        
        elif request.user.is_staffmember_has_profile():
            try:
                return RepresentativeSettings_Form(request, existing_profile = request.user.profile.get())
            except Exception as e:
                logger.exception("No existing profile found even tough it should be present.")
                messages.add_message(request, messages.WARNING, 'An error occurred, please submit the form again or contact us via mail.')
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
                messages.add_message(request, messages.INFO, 'Profile successfully created.')
                representative.staff_user.has_profile = True
                representative.staff_user.save()
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







def UserList(request):

    if request.user.is_authenticated and request.user.is_staffmember:

        companies_accepted = []
        companies_applied = []
        companies_notapplied = []
        staff_admin = []
        staff_moderator = []
        staff_viewer = []

        users = User.objects.all()

        for user in users:
            if user.is_company_is_accepted():
                companies_accepted.append(user)
            elif user.is_company_has_applied():
                companies_applied.append(user)
            elif user.is_company_has_not_applied():
                companies_notapplied.append(user)
            elif user.is_staffmember_is_admin():
                staff_admin.append(user)
            elif user.is_staffmember_is_moderator():
                staff_moderator.append(user)
            elif user.is_staffmember_is_viewer():
                staff_viewer.append(user)
            else:
                logger.exception("User %s does not have a valid identifier: %s." % (user, user.role))
                messages.add_message(request, messages.WARNING, "User %s does not have a valid identifier: %s." % (user, user.role))
                pass

        context = {
            'companies_accepted': companies_accepted, 
            'companies_applied': companies_applied, 
            'companies_notapplied': companies_notapplied,
            'staff_admin': staff_admin,
            'staff_moderator': staff_moderator,
            'staff_viewer': staff_viewer,
            'staff_accounts': len(staff_viewer)+len(staff_moderator)+len(staff_admin)
            }
        return render(request, 'profiles/userlist.html', context)


    else:
        return HttpResponseRedirect('/')


def StaffDetail(request, id):

    if request.user.is_authenticated and request.user.is_staffmember:

        this_user = User.objects.get(pk=id)

        try:
            context = {
                'representative': this_user.profile.get(),
                'user': this_user
                }
        except:
            logger.exception("User %s does not have a profile, but is was requested." % this_user)
            messages.add_message(request, messages.WARNING, "User %s does not have a profile, but is was requested." % this_user)
            context = {'user': this_user, 'representative': False}
        return render(request, 'profiles/staff_detail.html', context)


    else:
        return HttpResponseRedirect('/')







def CompanyList(request):

    if request.user.is_authenticated and request.user.is_staffmember:

        companies_accepted = []
        companies_applied = []

        companies = Company.objects.all()

        for company in companies:
            if company.company_user.is_company_is_accepted():
                companies_accepted.append(company)
            elif company.company_user.is_company_has_applied():
                companies_applied.append(company)
            elif company.company_user.is_company_has_not_applied():
                messages.add_message(request, messages.WARNING, "The user corresponding to company %s has the wrong role." % company)
                pass
            else:
                logger.exception("Company %s does not have a valid identifier: %s." % (company, company.company_user.role))
                messages.add_message(request, messages.WARNING, "User %s does not have a valid identifier: %s." % (company, company.company_user.role))
                pass

        context = {
            'companies_accepted': companies_accepted, 
            'companies_applied': companies_applied, 
            }
        return render(request, 'profiles/companylist.html', context)


    else:
        return HttpResponseRedirect('/')



def CompanyDetail(request, id):

    if request.user.is_authenticated and request.user.is_staffmember:

        this_company = Company.objects.get(pk=id)

        context = {'company': this_company, 'company_user': this_company.company_user, 'staff': this_company.staff_user}

        if request.user.is_staffmember_is_admin:
            context.update({
                'assign_staff_form': AssignStaffForm(initial={'company': id}),
                'accept_company_form': AcceptCompanyForm(initial={'company': id})
            })

        return render(request, 'profiles/company_detail.html', context)


    else:
        return HttpResponseRedirect('/')




def CompanyDetail_AssignStaffForm(request):

    if request.user.is_authenticated and request.user.is_staffmember_is_admin:

        # if a POST request
        if request.method == 'POST':

            form = AssignStaffForm(request.POST)

            if form.is_valid():

                company = form.cleaned_data['company']
                staff = form.cleaned_data['staff']

                company.staff_user = staff
                company.save()
                messages.add_message(request, messages.INFO, 'Staff assignment was successful.')
                return redirect('profiles:companydetail', id=company.pk)

            else:
                messages.add_message(request, messages.WARNING, 'Staff assignment was unsuccessful.')
                logger.error(form.errors)
                return redirect('profiles:companylist')


        # if a GET request
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/')



def CompanyDetail_AcceptCompanyForm(request):

    if request.user.is_authenticated and request.user.is_staffmember_is_admin:

        # if a POST request
        if request.method == 'POST':

            form = AcceptCompanyForm(request.POST)

            if form.is_valid():

                company = form.cleaned_data['company']
                check = form.cleaned_data['check']

                if check == company.title:
                    if company.company_user.promote_to_accepted_company():
                        company.company_user.save()
                        messages.add_message(request, messages.INFO, 'Company was successfully accepted.')
                        return redirect('profiles:companydetail', id=company.pk)

                    else:
                        messages.add_message(request, messages.WARNING, 'There was an error with the company account. Inform webmaster. No changes were made')
                        logger.error("Accepting of company %s failed due to user account issue." % company.title)
                        return redirect('profiles:companydetail', id=company.pk)

                else:
                    messages.add_message(request, messages.WARNING, 'You did not enter the company name correctly. No changes were made.')
                    logger.error("Accepting of company %s failed due to admin not passing company name check. Entered: %s" % (company.title, check))
                    return redirect('profiles:companydetail', id=company.pk)

            else:
                messages.add_message(request, messages.WARNING, 'There was an internal error. No changes were made.')
                logger.error(form.errors)
                return redirect('profiles:companylist')


        # if a GET request
        else:
            return HttpResponseRedirect('/')

    else:
        return HttpResponseRedirect('/')

