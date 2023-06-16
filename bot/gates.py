from bot.zadarma.api import ZadarmaAPI
from bot.config import zadarma_api_key, zadarma_api_secret, zadarma_number, zadarma_sip


z_api = ZadarmaAPI(key=zadarma_api_key, secret=zadarma_api_secret)


def call_number(to_number):
    return z_api.call(
        "/v1/request/callback/",
        {"from": zadarma_number, "to": to_number, "sip": zadarma_sip, "predicted": "1"},
    )
