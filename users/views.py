from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from .models import User
from .forms import UserEditForm


class OwnerMixin:
    def get_queryset(self):
        qs = super(OwnerMixin, self).get_queryset()
        return qs.objects.filter(user=self.request.user)
    # return qs.filter(id=self.request.user.id)
#   not in use for now


class OwnerEditMixin:
    def form_valid(self, form):
        if form.instance.id == self.request.user.id:
            return super(OwnerEditMixin, self).form_valid(form)
        return reverse('logout')
# Same as above, make sure this mixin works


class UserView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/view.html'
    pk_url_kwarg = 'id'


class UserEdit(LoginRequiredMixin, OwnerEditMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'users/edit.html'
    pk_url_kwarg = 'id'
