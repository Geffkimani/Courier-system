#This function sends an HTTP GET request with HTTP Basic authentication. 
# This function sends an HTTP GET request with HTTP Basic authentication. 
# It contacts the Safaricom endpoint to retrieve an access token, 
# which is required for any further API requests.It contacts the Safaricom endpoint to retrieve an access token, 
# which is required for any further API requests.

import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import base64
from datetime import datetime



def get_mpesa_access_token():
    response = requests.get(
        settings.ACCESS_TOKEN_URL,
        auth=HTTPBasicAuth(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    )
    response_json = response.json()
    return response_json.get("access_token")


def generate_lipa_na_mpesa_password():
    """
    Generates the password for the STK push by concatenating the BusinessShortCode,
    PASSKEY, and a timestamp, then encoding the result in Base64.
    Returns a tuple of (password, timestamp).
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = settings.SHORT_CODE + settings.PASSKEY + timestamp
    encoded_bytes = base64.b64encode(data_to_encode.encode('utf-8'))
    password = encoded_bytes.decode('utf-8')
    return password, timestamp