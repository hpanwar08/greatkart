from django import forms
from django.core.exceptions import ValidationError

from accounts.models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(required=True)

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password')

    def clean_phone_number(self):
        data = self.cleaned_data.get('phone_number')

        if not data.isnumeric():
            raise ValidationError('Phone number should contain only numbers')
        if len(data) != 10:
            raise ValidationError('Phone number should 10 digits')
        if len(data) > 10:
            raise ValidationError('Phone number should not be more than 10 digits')

        return data

    def clean(self):
        super().clean()
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')

        if password != password1:
            raise forms.ValidationError('Passwords do not match!')


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid': ("Image files only")},
                                       widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
