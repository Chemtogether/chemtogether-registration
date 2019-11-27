from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from captcha.fields import ReCaptchaField
User = get_user_model()


class SignupForm(UserCreationForm):

    email = forms.EmailField(max_length=200, help_text='Required. This email will only be used for verification.')
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')