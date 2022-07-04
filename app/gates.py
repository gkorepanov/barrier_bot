from zadarma.api import ZadarmaAPI
from config import ZADARMA_API_KEY, ZADARMA_API_SECRET, ZADARMA_NUMBER, GATE_NUMBERS, SIP


z_api = ZadarmaAPI(key=ZADARMA_API_KEY, secret=ZADARMA_API_SECRET)


def call_number(to_number):
    return z_api.call(
        "/v1/request/callback/",
        {"from": ZADARMA_NUMBER, "to": to_number, "sip": SIP, "predicted": "1"},
    )


def call_from(from_number, to_number):
    return z_api.call(
        "/v1/request/callback/",
        {"from": from_number, "to": to_number, "sip": SIP, "predicted": "1"},
    )


def open_gates(gates_name):
    return call_number(GATE_NUMBERS[gates_name])

