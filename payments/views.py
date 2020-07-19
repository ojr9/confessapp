from datetime import datetime
from django.shortcuts import render, HttpResponse
from django.template.response import TemplateResponse
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.dispatch import receiver

from allauth.account.signals import user_signed_up
from mangopay.constants import EVENT_TYPE_CHOICES

from .models import MangoNaturalUser, MangoWallet, MangoWebPayIn, MangoCardDirectPayIn, MangoCardRegistration, \
    MangoEvents, MangoDDWebPayIn, MangoBankAccount, MangoCard, MangoPayIn
from .forms import BankAccountForm
"""
These are helper views, not to be used in the actual ones in other apps. 
The idea is to embed objects in the views and call methods from there and the templates.
"""
usr = get_user_model()


@receiver(user_signed_up)
def setup_user(request, **kwargs):
    user = kwargs['user']
    # Create the MGP user:
    newnaturaluser = MangoNaturalUser(user=user)
    newnaturaluser.create()  # dummy data on BD, CoR, Nat.
    # Create the MGP Wallet:
    wallet = MangoWallet(mid=newnaturaluser.mid)
    wallet.create()


class ViewPurse(LoginRequiredMixin, generic.TemplateView):
    template_name = 'bank/detail.html'

    def get_context_data(self, **kwargs):
        context = super(ViewPurse, self).get_context_data()
        mid = MangoNaturalUser.objects.get(user=self.request.user).mid
        context['transactions'] = MangoPayIn.objects.filter(author_id=mid)
        context['wallet'] = MangoWallet.objects.get(mid=mid)
        context['bankaccounts'] = MangoBankAccount.objects.filter(mid=mid)
        return context


def testgetter(request):
    print('Getting user')
    user = request.user
    print('getting mang user')
    muser = MangoNaturalUser.objects.get(user=user)
    print('mid is', muser.mid)
    return HttpResponse(muser.mid)




class CreateBankAccount(generic.CreateView):
    model = MangoBankAccount
    form_class = BankAccountForm
    template_name = 'bank/create.html'

    def form_valid(self, form):
        cd = form.cleaned_data
        user = self.request.user
        self.object.create(user=user, line1=cd['line1'], line2=cd['line2'], city=cd['city'], region=cd['region'],
                           pc=cd['pc'], country=['country'])
        return super().form_valid(form)


class CardsList(LoginRequiredMixin, generic.ListView):
    model = MangoCard
    template_name = 'payments/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        user = self.request.user
        mid = MangoNaturalUser.objects.get(user=user).mid
        qs = MangoCard.objects.filter(mid=mid)
        return super(CardsList, self).get_queryset(qs)


@login_required
def cardRegistration(request, currency, card_type):
    user = request.user
    mid = MangoNaturalUser.objects.get(user=user).mid
    card_registration = MangoCardRegistration(mid, currency, card_type)
    preregdata = card_registration.create()
    return TemplateResponse(request, 'mangopay_test.html', context=preregdata)


# Should be the last one:
class MangoHookHandler(generic.View):

    def post(self, request, ev, resid, tmp):
        if ev in EVENT_TYPE_CHOICES:
            # Check if it is still relevant and truly from mgp
            # this check for relevant status hmmm should ideally be a 'view' method in each of the classes, next to the create.
            # Create the event record and dispatch
            time = datetime.fromtimestamp(tmp)
            event = MangoEvents.objects.create(event=ev, resid=resid, created=time)
            # make this a celery task to speed this up
            # event.verify()
            event.dispatch()
            if event.authentic:
                return HttpResponse(status=200)
