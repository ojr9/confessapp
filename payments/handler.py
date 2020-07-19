import mangopay
from mangopay.api import APIRequest
from mangopay.auth import StaticStorageStrategy

from django.conf import settings

mangopay.client_id = settings.MANGOPAY_CLIENTID
mangopay.sandbox = settings.DEBUG
if mangopay.sandbox:
    mangopay.apikey = settings.MANGOPAY_SANDBOX_ID
else:
    mangopay.apikey = settings.MANGOPAY_PROD_ID

handler = APIRequest(sandbox=True, storage_strategy=StaticStorageStrategy(), timeout=30.0)


def get_handler():
    return handler
