from django import forms

from .models import MangoBankAccount


class BankAccountForm(forms.Form):
    iban = forms.CharField()
    bic = forms.CharField(required=False)
    line1 = forms.CharField()
    line2 = forms.CharField(required=False)
    city = forms.CharField()
    region = forms.CharField(required=False)
    pc = forms.CharField()
    country = forms.CharField()
