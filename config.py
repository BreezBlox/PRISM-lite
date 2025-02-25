import os

DEPARTMENTS = [
    'Engineering',
    'Supply Chain',
    'Metal Shop',
    'Pre-Assembly',
    'Bodywork',
    'Paint',
    'Final Assembly',
    'Sign-Shop/Graphic Design',
    'Shipping'
]

MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY', 'dummy-key')
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

DATABASE_URL = "sqlite:///production_delays.db"
