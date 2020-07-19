from decimal import Decimal, ROUND_FLOOR
import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.http import HttpResponse

"""
    This is the model to integrate your first mangopay app. Good luck!
"""
from mangopay.fields import MoneyField, AddressField
from mangopay.utils import Money, Address, timestamp_from_datetime, timestamp_from_date
from mangopay.resources import User, NaturalUser, Wallet, CardWebPayIn, DirectDebitDirectPayIn, Document, Page, \
    BankWirePayOut, PayInRefund, BankAccount, Card, CardRegistration, BankWirePayIn, DirectDebitWebPayIn, \
    Transfer, BankingAliasIBAN
from mangopay.constants import USER_TYPE_CHOICES, CARD_TYPE_CHOICES, PAYMENT_STATUS_CHOICES, PAYIN_PAYMENT_TYPE


usr = get_user_model()


def amount_and_currency_to_mangopay_money(amount, currency):
    amount = amount.quantize(Decimal('.01'), rounding=ROUND_FLOOR) * 100
    return Money(amount=int(amount), currency=currency)


def _make_address(line1, line2, city, pc, country, region=None):
    return Address(line1, line2, city, region, pc, country)


def _date_from_timestamp(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


class MangoUser(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    last_edit = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(usr, on_delete=models.PROTECT, related_name='%(class)s_mango_user')
    usertype = models.CharField(max_length=7, choices=USER_TYPE_CHOICES)
    mid = models.PositiveIntegerField(default=0)
    # Light KYC
    birthday = models.DateField()
    nationality = models.CharField(max_length=50, default='DE') #Get a country field from a package
    country_of_residence = models.CharField(max_length=50, default='DE') #Same here
    # Regular KYC stuff
    kyc_status = models.BooleanField(default=False)
    # ehh what again ?

    def get_wallets(self):
        user = User.get(self.mid)
        return [user.wallets]

    def _check_validation(self):
        return self.kyc_status

    @staticmethod
    def _update_user(date):
        return timestamp_from_date(date)

    class Meta:
        ordering = ['-created']


class MangoNaturalUser(MangoUser):

    def create(self): # check if not to pass in the user from the request in the view
        self.birthday = _date_from_timestamp(1)
        mango_call = NaturalUser(FirstName=self.user.first_name, LastName=self.user.last_name, Email=self.user.email,
                                 Birthday=1, Nationality=self.nationality,
                                 CountryOfResidence=self.country_of_residence)
        mango_call.save()
        self.usertype = 'NATURAL'
        self.mid = mango_call.get_pk()
        print(self.birthday)
        print(type(self.birthday))
        self.save()

    def __str__(self):
        return f'{self.mid} : {self.user} - N'

    def is_validated(self):
        return self.kyc_status


class MangoLegalUser(MangoUser):
    pass


class MangoWallet(models.Model):
    # owner = models.ForeignKey(MangoNaturalUser, on_delete=models.PROTECT) So!!! some obj are loose from the user in
    # question. Not sure if I forgot or there was a definite reason. There is a compelling reason for the model utils
    # manager to be used in this. As some objs are linked like wallets to natural users to musers to users....
    wid = models.PositiveIntegerField(default=0)
    mid = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='EUR')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    iban = models.CharField(max_length=50, blank=True, null=True)
    bic = models.CharField(max_length=12, blank=True, null=True)
    alias_country = models.CharField(max_length=2, default='LU')

    def create(self):
        wallet_call = Wallet(Owners=[self.mid], Description=f'Wallet for {self.mid}', currency=self.currency)
        wallet_call.save()
        self.wid = int(wallet_call.get_pk())
        self.save()

    def get_balance(self):
        wallet = Wallet.get(self.wid)
        if self.balance != wallet.Balance.Amount / 100:
            self.balance = wallet.Balance.Amount / 100
            self.save()
        return self.balance, self.currency

    def __str__(self):
        return f'Wallet {self.wid} from {self.mid}'

    def ibanize(self):
        owner = MangoUser.objects.get(mid=self.mid)
        name = str(owner.user.first_name + owner.user.last_name)
        alias = BankingAliasIBAN(WalletId=self.wid, OwnerName=name, Country='LU')
        alias.save()
        self.iban = alias['IBAN']
        self.bic = alias['BIC']
        self.save()
        # When more vIBANs are there update to choose from them


class MangoCardRegistration(models.Model):
    mid = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='mango_card_reg')
    currency = models.CharField(max_length=3, default='EUR')
    card_type = models.CharField(max_length=20, default=CARD_TYPE_CHOICES['CB_VISA_MASTERCARD'])

    def create(self):
        # Currently only registers CB_VISA_MC....
        registration = CardRegistration(UserId=self.mid, Currency=self.currency, CardType=self.card_type)
        print(registration)
        registration.save()
        # Create the card that will hold all the data once registration is done
        card = MangoCard(mid=self.mid, is_valid=True)
        card.save()
        # Now the preregistration data should be in the 'registration' variable. Passing this back to the view.
        preregdata = {'accessKey': registration['AccessKey'], 'preregistrationdata': registration['preregistrationData'],
                      'cardRegistrationURL': registration['cardRegistrationURL']}
        return preregdata
        # id = registration.mid


class MangoCard(models.Model):
    cid = models.PositiveIntegerField(default=0)
    mid = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='mango_card')
    expiration_date = models.PositiveSmallIntegerField(default=0)
    currency = models.CharField(max_length=3, default='EUR')
    alias = models.CharField(max_length=20, default='')
    provider = models.CharField(max_length=15, default='')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    is_active = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    creation_date = models.PositiveIntegerField(default=0) #this needs to change to a date field that gets a time stamp
    fingerprint = models.CharField(max_length=100, default='call update function')

    # deleted = models.BooleanField(default=False) this was extra in the integration example
    def deactivate(self):
        # card = Card.get(self.cid)
        # do I have to make a custom call here to deactivate?? where is the function in the sdk??
        pass

    def list_all_user_cards(self):
        pass

    def update(self):
        # Am I getting here the first cid? then no if
        if self.cid:
            card = Card.get(self.cid)
            self.expiration_date = card['ExpirationDate']
            self.alias = card['Alias']
            self.provider = card['CardProvider']
            self.currency = card['Currency']
            if card['Active'] == '':
                self.is_active = True
            if card['Validity'] == 'VALID':
                self.is_valid = True
            self.creation_date = card['CreationDate']
            self.fingerprint = card['fingerprint']
            self.card_type = card['CardType']
            self.save()

    def is_expired(self):
        month = self.expiration_date[:2]
        year = self.expiration_date[2:]
        current_month = datetime.datetime.utcnow().month
        current_year = int(str(datetime.datetime.utcnow().year)[2:])
        if current_year > year:
            return True
        if current_year == year and current_month >= month:
            return True
        return False

    def __str__(self):
        return f'{self.cid} from {self.mid}'


class MangoPreAuth(models.Model):
    pass
# requires a working registered card


class MangoPayIn(models.Model):
    piid = models.PositiveIntegerField(default=0)
    creation_date = models.DateTimeField()
    author_id = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='%(class)s_mango_payin_author')
    cwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='%(class)s_mango_payin_cwid')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    culture = models.CharField(max_length=2, default='EN')
    statement_descriptor = models.CharField(max_length=12, default='')
    status = models.CharField(max_length=9, choices=PAYMENT_STATUS_CHOICES, default='CREATED')
    result_code = models.CharField(max_length=6, null=True, blank=True)
    result_message = models.CharField(max_length=255, null=True, blank=True)
    # execution_date
    nature = models.CharField(max_length=10, default='')
    transaction_type = models.CharField(max_length=10)

    class Meta:
        ordering = ['creation_date']


class MangoWebPayIn(MangoPayIn):
    return_url = models.URLField(default='someurl.com/') # My return url to redirect to, after the payment, people will be sent there...
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='CB_VISA_MASTERCARD')
    secure_mode = models.BooleanField(default=True)
    money = MoneyField()

    def _check_payin(self, payin):
        # depending if the result code is  200 or not, recall method and change function
        pass

    def retry(self):
        # depending on the result codes, some logic here to retry or not.
        pass

    def create(self, user):
        # Only CB_VISA_MC is accepted for now
        if self.amount < 30:
            self.secure_mode = False
        mid = MangoUser.objects.get(user=user).mid
        wallet = MangoWallet.objects.get(mid=mid)
        payin = CardWebPayIn(AuthorId=mid,
                             DebitedFunds= Money(self.amount*100, self.currency),
                             Fees=Money(int(self.fees*100), self.currency),
                             ReturnURL=self.return_url,
                             CardType=self.card_type,
                             CreditedWalletId=wallet,
                             SecureMode=self.secure_mode,
                             Culture=self.culture,
                             TemplateURLOptions={'PaylineV2': ''},
                             StatementDescriptor=self.statement_descriptor)
                            # check if the Money fuction works like this.
        # if payin.status == 'FAILED':
        #    check = _check_payin(payin) marks unresolved ref??

        # Need to make a template and view to receive the user after the payment
        # Check to see if these dictionaries are workiing the way they should, intuitively they should. Or use the helper func
        # also should I dump the answer from json into a dict?? Like I read?
        payin.save()
        self.piid = payin.get_pk()
        self.creation_date = payin.execution_date
        self.result_code = payin.result_code
        self.result_message = payin.result_message
        self.return_url = payin.return_url
        self.nature = payin.nature
        self.save()

    def __str__(self):
        return f'{self.piid} and other similar stuff'


class MangoCardDirectPayIn(MangoPayIn):
    pass


class MangoBankWirePayIn(MangoPayIn):
    execution_type = models.CharField(max_length=50)
    wire_reference = models.CharField(max_length=50)
    # Bank account
    # BA1: Owner address
    address = AddressField()
    # addressline1 = models.CharField(max_length=250)
    # addressline2 = models.CharField(max_length=250)
    # city = models.CharField(max_length=50)
    # region = models.CharField(max_length=50, blank=True, null=True)
    # postal_code = models.CharField(max_length=10)
    # country = models.CharField(max_length=2) # have to change this to a country field that can understand.
    wire_type = models.CharField(max_length=5)
    iban = models.CharField(max_length=50) # Need to change this to an IBAN field, same as above.
    bic = models.CharField(max_length=25)

    def create(self, user, amount, fees, line1, line2, city, pc, country):
        address = _make_address(line1, line2, city, pc, country)
        mid = MangoUser.objects.get(user=user).mid
        wallet = MangoWallet.objects.get(mid=mid).wid
        bw = BankWirePayIn(AuthorId=mid, CreditedWalletId=wallet,
                           DeclaredDebitedFunds=Money(amount, wallet.currency),
                           DeclaredFees=Money(fees, wallet.currency))
        bw.save()
        self.piid = bw.get_pk()
        self.creation_date = bw['CreationDate']
        self.status = 'CREATED'
        self.amount = amount
        self.fees = fees
        self.transaction_type = bw['BANK_WIRE']
        self.wire_reference = bw['WireReference']
        self.address = address
        self.wire_type = bw['Type']
        self.iban = bw['IBAN']
        self.bic = bw['BIC']
        self.save()

    def _check_status(self):
        bw = BankWirePayIn.get(Id=self.piid)
        if bw.status != self.status:
            self.status = bw.status
        return self.status

    def __str__(self):
        return f'{self.piid} BW on {self.creation_date} - {self.status}'


class MangoDDWebPayIn(MangoPayIn):
    direct_debit_type = models.CharField(max_length=7, default='SOFORT')
    return_url = models.URLField()
    redirect_url = models.URLField(blank=True, null=True)
    template_url = models.URLField()

    def create(self, user):
        author = MangoUser.objects.get(user=user)
        wallet = MangoWallet.objects.get(mid=author.mid) # Here I can also filter by currency when the time comes
        ddweb = DirectDebitWebPayIn(AuthorId=author.mid,
                                    DebitedFunds=Money(self.amount, wallet.currency),
                                    Fees=Money(self.fees, wallet.currency), ReturnURL=self.return_url,
                                    CreditedWalletId=wallet.wid, DirectDebitType=self.direct_debit_type,
                                    Culture=self.culture)
        ddweb.save()
        self.piid = ddweb.get_pk()
        self.template_url = ddweb['TemplateURL']
        self.creation_date = ddweb['CreationDate']
        self.author_id = author.mid
        self.cwid = wallet.wid
        self.status = ddweb['Status']
        self.save()
        return ddweb


class MangoRefund(models.Model):
    pass


class MangoTransfer(models.Model):
    tid = models.PositiveIntegerField()
    creation_date = models.DateTimeField()
    author = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='transfer_author')
    recipient = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='transfer_recipient')
    dwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='debited_wallet_id')
    cwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='credited_wallet_id') # Do I stillneed this rel name?
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    fees = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=9) # Add choices from the constant
    result_code = models.CharField(max_length=6, null=True, blank=True)
    result_message = models.CharField(max_length=255, null=True, blank=True)

    # Do I need this method if the api is checking too? More like a error resolution method instead?
    def verify(self, author, recipient):
        try:
            sender_wallet = MangoWallet.objects.get(user=author).wid
            assert MangoUser.objects.get(user=recipient).wid
            assert sender_wallet.balance >= self.amount + self.fees
        except AssertionError('Please check your input again. Do you have enough funds?'):
            return False
        return True

    def create(self, author, recipient, amount):
        sender = MangoUser.objects.get(user=author)
        receiver = MangoUser.objects.get(user=recipient)
        swid = MangoWallet.objects.get(mid=sender.mid).wid
        credwallet = MangoWallet.objects.get(mid=receiver.mid).wid
        rwid = credwallet.wid
        self.currency = credwallet.currency
        transfer = Transfer(AuthorId=sender.mid, DebitedFunds=Money(amount, self.currency),
                            Fees=Money(self.fees, self.currency), DebitedWalletId=swid,
                            CreditedWalletId=rwid)
        transfer.save()

        self.tid = transfer.get_pk()
        self.creation_date = transfer.execution_date
        self.author = sender.mid
        self.recipient = receiver.mid
        self.dwid = transfer.DebitedWalletId
        self.cwid = transfer.CreditedWalletId
        self.amount = amount
        self.status = transfer.status
        self.result_code = transfer.result_code
        self.result_message = transfer.result_message
        self.save()


def get_fees(amount):
    return amount * 0.07
# Of course this could be a nicer, more flexibility offering function. What cases charge what idea...


def extra_charge_from_wallet(request):
    pass


class MangoDocument(models.Model):
    doc_type = models.CharField(max_length=23, default='IDENTITY_PROOF')
    did = models.PositiveIntegerField(default=0)
    mid = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='mango_document')
    creation_date = models.DateTimeField()
    processed_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9)
    refusal_type = models.CharField(max_length=25, blank=True, null=True)
    refusal_message = models.CharField(max_length=250, blank=True, null=True)

    def create(self, user):
        mid = MangoUser.objects.get(user=user).mid
        self.mid = mid
        document = Document(user=mid, Type=self.doc_type)
        document.save()
        self.did = document.get_pk()
        self.creation_date = document.CreationDate
        self.status = 'CREATED'
        self.save()

    def validate(self):
        if self.status is 'CREATED':
            document = Document.get(id=self.did)
            document.status = 'VALIDATION_ASKED'
            document.save()
            self.status = document.status
            self.save()
        else:
            raise BaseException('Cannot ask validation if not in created status')

    def update(self):
        pass
        # make an update function or more a receiver of the hook receiver?


class MangoPage(models.Model):
    doc = models.ForeignKey(MangoDocument, on_delete=models.CASCADE, related_name='mango_page')
    paid = models.PositiveIntegerField()

    @staticmethod
    def _check_extention(filename):
        pass

    def create(self, file):
        document = Document.get(id=self.doc.did)

        page = Page(user=self.doc.mid, document=document, file=file)
        page.save()
        self.paid = page.get_pk()
        self.save()


class MangoUBODeclaration(models.Model):
    pass


class MangoBankAccount(models.Model):
    bid = models.PositiveIntegerField()
    mid = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='mango_bank_account')
    iban = models.CharField(max_length=35)
    bic = models.CharField(max_length=20, null=True, blank=True)
    address = AddressField()
    # addressline1 = models.CharField(max_length=250)
    # addressline2 = models.CharField(max_length=250)
    # city = models.CharField(max_length=50)
    # region = models.CharField(max_length=50, default='')
    # postal_code = models.CharField(max_length=10)
    # country = models.CharField(max_length=2)
    bank_account_type = models.CharField(max_length=10, default='IBAN')
    creation_date = models.DateTimeField()
    active = models.BooleanField()

    def create(self, user, line1, city, region, pc, country, line2=''):
        self.mid = MangoUser.objects.get(user=user).mid
        address = _make_address(line1, line2, city, pc, country, region)
        self.address = address
        ba = BankAccount(OwnerAddress=address, OwnerName=(str(user.first_name + user.last_name)), IBAN=self.iban,
                         BIC=self.bic)
        # check if I don't need a function in the user model for get_full_name
        ba.save()
        self.bid = ba.get_pk()
        self.creation_date = ba.creation_date
        self.active = True
        self.save()

    def deactivate(self):
        ba = BankAccount.get(Id=self.bid)
        ba.deactivate()
        ba.save()
        self.active = False
        self.save()
        return HttpResponse('Bank Account deactivated.')


class MangoPayOut(models.Model):
    poid = models.PositiveIntegerField()
    author_id = models.ForeignKey(MangoUser, on_delete=models.PROTECT, related_name='mango_payout_author_id')
    bid = models.ForeignKey(MangoBankAccount, on_delete=models.PROTECT, related_name='mango_bankaccount')
    dwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='mango_debited_wallet_id')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    fees = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    reference = models.CharField(max_length=50, null=True, blank=True)
    creation_date = models.DateTimeField()
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=15, default='CREATED')
    result_code = models.PositiveIntegerField(null=True, blank=True)
    result_message = models.CharField(max_length=250, null=True, blank=True)

    def create(self, user):
        # call the _check here
        mid = MangoUser.objects.get(user=user).mid
        bid = MangoBankAccount.objects.get(mid=mid)
        dwid = MangoWallet.objects.get(mid=mid)
        payout = BankWirePayOut(AuthorId=mid, DebitedFunds=Money(self.amount, self.currency),
                                Fees=Money(self.fees, self.currency), BankAccountId=bid,
                                DebitedWalletId=dwid, BankWireRef=self.reference)
        payout.save()
        self.poid = payout.get_pk()
        self.author_id = mid
        self.bid = bid
        self.dwid = dwid
        self.creation_date = payout['CreationDate'] # is this form ok?
        self.save()
        # Or add a logic in case of failed payouts?

    def _check_validation(self):
        # should include user validation status and if documents are currently being treated?
        pass

    def status_update(self):
        payout = BankWirePayOut.get(Id=self.poid)
        if self.status == payout.status:
            return self.status
        self.status = payout.status
        self.execution_date = payout['ExecutionDate']
        self.save()
        return self.status

    def __str__(self):
        return f'{self.poid} - '


class MangoTransaction(models.Model):

    creation_date = models.DateTimeField()
    cwid = models.ForeignKey(MangoWallet, on_delete=models.PROTECT, related_name='%(class)s_mango_payin_cwid')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    fees = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    culture = models.CharField(max_length=2, default='EN')
    statement_descriptor = models.CharField(max_length=12, default='')
    status = models.CharField(max_length=9, choices=PAYMENT_STATUS_CHOICES, default='CREATED')
    result_code = models.CharField(max_length=6, null=True, blank=True)
    result_message = models.CharField(max_length=255, null=True, blank=True)
    # execution_date
    nature = models.CharField(max_length=10, default='')
    transaction_type = models.CharField(max_length=10)

    def update(self, mid):
        # make an update from the API on the transactions a user has done. Not sure this is something to save in the DB or not...
        pass

class MangoEvents(models.Model):
    event = models.CharField(max_length=50)
    resid = models.PositiveIntegerField
    created = models.DateTimeField()
    authentic = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.event} - {self.resid}'

    def verify(self):
        # This verifies that the event is real, how?
        pass

    def dispatch(self):
        # Define what type of resource is being talked about
        main, verb = self.event.split('_', 1)
        if main not in ('KYC', 'PAYIN', 'PAYOUT', 'TRANSFER', 'MANDATE'):
            self.authentic = False
            self.save()
            return False
        if main == 'KYC':
            obj = MangoDocument.objects.get(did=self.resid)
            # call in a validation status function
            # if verb == 'VALIDATION_ASKED' and obj.status == 'CREATED':
            #     obj.status = 'VALIDATION_ASKED'
            #     obj.save()
        if main == 'PAYIN':
            v1, v2 = verb.split('_')
            if v1 == 'NORMAL':
                pin = MangoPayIn.objects.get(piid=self.resid)
                # Do something with the message in v2
            else:
                pass # Then it has to be a refund that those are not in yet.
        if main == 'PAYOUT':
            v1, v2 = verb.split('_')
            if v1 == 'NORMAL':
                pot = MangoPayOut.objects.get(poid=self.resid)
                # Do something with the message in v2
            else:
                pass  # Then it has to be a refund that those are not in yet.
        if main == 'TRANSFER':
            v1, v2 = verb.split('_')
            if v1 == 'NORMAL':
                trfr = MangoTransfer.objects.get(tid=self.resid)
                # Do something with the message in v2
            else:
                pass  # Then it has to be a refund that those are not in yet.
        if main == 'MANDATE':
            pass # this has just 1 verb but is not implemented at all....


class Alerts(models.Model):
    class Meta:
        abstract = True
# This is for logging events adn stuff that require manual inspection, flags in the system so to say.
# Triggers to create such an entry should be spread in the other models and views.
