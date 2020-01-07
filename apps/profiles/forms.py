from django.forms import ModelForm
from .models import Company, Representative



class ApplicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['accepts_tos'].required = True

    class Meta:
        model = Company
        fields = ['title', 'day', 'package', 'first_name', 'last_name', 'email', 'phone_number', 'language', 'mailing_address', 'billing_address', 'comments','accepts_tos']



class RepresentativeForm(ModelForm):

    class Meta:
        model = Representative
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'image']










