from django import forms
from django.db.models.base import Model
from django.forms import fields
from users.models import Profile


class ProfileModelForm(forms.ModelForm):

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = Profile
        fields = ('first_name','last_name','bio')


class ProfileImageModelForm(forms.ModelForm):

    profile = forms.ImageField(widget=forms.FileInput
        (attrs={ 'class': 'form-control','multiple':'true','style':'display:none'}),required=True)

    class Meta:
        model = Profile
        fields = ('profile',)