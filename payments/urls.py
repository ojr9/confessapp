from django.urls import path

from .views import cardRegistration, ViewPurse, CreateBankAccount, MangoHookHandler, testgetter


urlpatterns = [
    path('newbankaccount/', CreateBankAccount.as_view(), name='new_bankaccount'),
    path('', ViewPurse.as_view(), name='purse'),


    # Hooks Url
    path('hooks/', MangoHookHandler.as_view(), {'EventType': 'ev', 'ResourceId': 'resid', 'Timestamp': 'tsp'},
         name='hook_receiver'),
    path('hooks2/', MangoHookHandler.as_view(), name='hooks2'),
]