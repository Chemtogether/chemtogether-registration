from django.forms import Form, ModelForm, ModelChoiceField, HiddenInput, CharField, ChoiceField
from .models import Company, Representative
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import StrictButton



class ApplicationForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['accepts_tos'].required = True

    class Meta:
        model = Company
        fields = ['title', 'day', 'flexible_day','package', 'flexible_package', 'first_name', 'last_name', 'email', 'phone_number', 'language', 'mailing_address', 'billing_address', 'comments','accepts_tos']



class RepresentativeForm(ModelForm):

    class Meta:
        model = Representative
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'image']


class AssignStaffForm(Form):

    def __init__(self, *args, **kwargs):
        super(AssignStaffForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        self.helper.form_method = 'post'
        self.helper.form_action = 'profiles:assignstaff'
        self.helper.add_input(Submit('submit', 'Assign'))
        self.helper.layout = Layout(
            'company',
            'staff',
        )

    company = ModelChoiceField(queryset = Company.objects.all(), widget = HiddenInput(), required = True)
    staff = ModelChoiceField(queryset = Representative.objects.all(), required = True)


class AcceptCompanyForm(Form):

    def __init__(self, *args, **kwargs):
        super(AcceptCompanyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap4/layout/inline_field.html'
        self.helper.form_method = 'post'
        self.helper.form_action = 'profiles:acceptcompany'
        self.helper.add_input(Submit('submit', 'Accept Company'))
        self.helper.layout = Layout(
            'company',
            'day',
            'package',
            'check',
        )

    check = CharField(label = "Check: enter company name", required = True)
    day = ChoiceField(label = "Select fair day", required = True, choices=((1, 'Tuesday'),(2, 'Wednesday')))
    package = ChoiceField(label = "Select package", required = True, choices=(
            (0, "Base"),
            (1, "Silver"),
            (2, "Gold"),
            (3, "Platinum"),
        )
    )
    company = ModelChoiceField(queryset = Company.objects.all(), widget = HiddenInput(), required = True)



