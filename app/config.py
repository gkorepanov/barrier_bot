from environs import Env

env = Env()

ZADARMA_API_KEY = env("ZADARMA_API_KEY")
ZADARMA_API_SECRET = env("ZADARMA_API_SECRET")

TELEGRAM_API_TOKEN = env("TELEGRAM_API_TOKEN")

ZADARMA_NUMBER = env("ZADARMA_NUMBER")
SIP = env("SIP")

GATE_NAMES = env("GATE_NAMES").split(",")

GATE_NUMBERS = {
    name: number
    for name, number
    in zip(GATE_NAMES, env("GATE_NUMBERS").split(","))
}

