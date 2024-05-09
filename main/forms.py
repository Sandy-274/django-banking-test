from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from datetime import date
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.forms.widgets import PasswordInput, TextInput
from .models import CustomUser, AccountInfo
import re

class CreateUserForm(UserCreationForm):

    class Meta:

        model=CustomUser
        fields=['username','email','dob','password1','password2']
        labels = {
            'dob': 'Date of Birth',
        }
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 18:
                raise forms.ValidationError("You must be at least 18 years old to register.")
        return dob

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=150)
    password= forms.CharField(widget=PasswordInput())
    

class AccountInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance')
        super(AccountInfoForm, self).__init__(*args, **kwargs)

    def clean_aadhar_number(self):
        aadhar_number = self.cleaned_data['aadhar_number']
        if len(aadhar_number) != 12 or not aadhar_number.isdigit():
            raise ValidationError("Enter a valid Aadhaar Number")

        existing_accounts = AccountInfo.objects.exclude(pk=self.instance.pk) if self.instance else AccountInfo.objects.all()
        if existing_accounts.filter(aadhar_number=aadhar_number).exists():
            raise ValidationError("A user with this Aadhaar number already exists.")
        return aadhar_number
    
    def clean_pan_number(self):
        pan_number = self.cleaned_data['pan_number']
        if not re.match(r'^[A-Z]{5}\d{4}[A-Z]$', pan_number):
            raise forms.ValidationError("Enter a valid PAN number.")

        existing_accounts = AccountInfo.objects.exclude(pk=self.instance.pk) if self.instance else AccountInfo.objects.all()
        if existing_accounts.filter(pan_number=pan_number).exists():
            raise ValidationError("A user with this PAN number already exists.")

        return pan_number

    class Meta:
        model = AccountInfo
        fields = ('account_holder_name', 'pan_number', 'aadhar_number', 'gender')
        labels = {
            'account_holder_name': 'Account Holder Name',
            'pan_number': 'PAN Number',
            'aadhar_number': 'Aadhaar Number',
            'gender': 'Gender',
        }


class TransactionFilterForm(forms.Form):
    start_date = forms.DateField(label='Start Date', required=False)
    end_date = forms.DateField(label='End Date', required=False)