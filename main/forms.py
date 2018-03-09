from django import forms
from django.contrib.auth import forms as auth_forms


invalid_error = 'User with this {} already exists.'


class LoginForm(auth_forms.AuthenticationForm):

    username = forms.CharField(max_length=254,
                               widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'required': 'True',
                                                             'placeholder': 'Username...'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                 'required': 'True',
                                                                 'placeholder': 'Password...'}))
    next_ = forms.CharField(widget=forms.HiddenInput())


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file'
    )