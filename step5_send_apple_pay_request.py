# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import hashlib
import json
import requests
import uuid

from config import BIZ_ID, BUSINESS_CHAT_SERVER, IMESSAGE_EXTENSION_BID
from jwt_util import get_jwt_token

APPLE_PAY_MERCHANT_SESSION_GATEWAY = "https://apple-pay-gateway.apple.com/paymentservices/paymentSession"

MY_MERCHANT_ID = "merchant.com.cequens.app1"
MY_DOMAIN_NAME = "webchat.cequens.net"
MY_MERCHANT_NAME = "Cequens Testing"

MY_PEM_FILE_PATH = "s.omar-cequens.crt.pem"
MY_PAYMENT_GATEWAY_URL = "https://apple-cequens-api-heroku.herokuapp.com/paymentGateway"


def get_apple_pay_merchant_session():
    payload = json.dumps({
        "merchantIdentifier": hashlib.sha256(MY_MERCHANT_ID.encode('utf-8')).hexdigest(),
        "displayName": MY_MERCHANT_NAME,
        "initiative": "messaging",
        "initiativeContext": MY_PAYMENT_GATEWAY_URL
    })

    headers = {'content-type': 'application/json'}

    response = requests.request("POST",
                                APPLE_PAY_MERCHANT_SESSION_GATEWAY,
                                data=payload,
                                headers=headers,
                                cert=MY_PEM_FILE_PATH)

    merchant_session = json.loads(response.text)
    return merchant_session


def send_apple_pay_request(destination_id):
    message_id = str(uuid.uuid4())  # generate unique message id
    request_id = str(uuid.uuid4())  # generate unique request id

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % get_jwt_token(),
        "id": message_id,
        "Source-Id": BIZ_ID,
        "Destination-Id": destination_id
    }

    payload = {
        "v": 1,
        "type": "interactive",
        "id": message_id,
        "sourceId": BIZ_ID,
        "destinationId": destination_id,
        "interactiveData": {
            "receivedMessage": {
                "style": "icon",
                "title": "Payment Title",
                "subtitle": "Payment Subtitle"
            },
            "bid": IMESSAGE_EXTENSION_BID,
            "data": {
                "requestIdentifier": request_id,
                "mspVersion": "1.0",
                "payment": {
                    "paymentRequest": {
                        "lineItems": [
                            {
                                "label": "Item 1",
                                "amount": "10.00",
                                "type": "final"
                            }
                        ],
                        "total": {
                            "label": "Your Total",
                            "amount": "10.00",
                            "type": "final"
                        },
                        "applePay": {
                            "merchantIdentifier": MY_MERCHANT_ID,
                            "supportedNetworks": [
                                "amex",
                                "visa",
                                "discover",
                                "masterCard",
                                "chinaUnionPay",
                                "interac",
                                "privateLabel"
                            ],
                            "merchantCapabilities": [
                                "supportsDebit",
                                "supportsCredit",
                                "supportsEMV",
                                "supports3DS"
                            ]
                        },
                        "merchantName": MY_MERCHANT_NAME,
                        "countryCode": "US",
                        "currencyCode": "USD",
                        "requiredBillingContactFields": [],
                        "requiredShippingContactFields": []
                    },
                    "merchantSession": get_apple_pay_merchant_session(),
                    "endpoints": {
                        "paymentGatewayUrl": MY_PAYMENT_GATEWAY_URL
                    }
                }
            }
        }
    }

    r = requests.post("%s/message" % BUSINESS_CHAT_SERVER,
                      json=payload,
                      headers=headers,
                      timeout=10,verify=False)

    print("Business Chat server return code: %s" % r.status_code)


if __name__ == "__main__":
    destination_id = "urn:mbid:AQAAY63/TIJe/3nF4EvsJeiA+WeopPR92ycuqyjDzc/14u/PdDhLVjieuzb5nPPwFB9u8jXUS/um2flw2Jr5SKGpDHHGstPdM9TyV0Ml5lldZ/nanUpHWMbBn5AwD3FpoqWhOP0t+5oCWvZaMCtdIPNsgFIaZEA="
    send_apple_pay_request(destination_id)

# Expected output:
# Business Chat server return code: 200
