from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django import forms


class UserCreateForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    def signup(self, request, user):
        return user


class UserEditForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')

        # Others will be definitely added to start the wallet process
