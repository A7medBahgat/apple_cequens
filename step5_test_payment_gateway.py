# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import json
from flask import Flask, request

app = Flask(__name__)


@app.route("/paymentGateway", methods=['POST'])
def process_payment():
    payment_payload = json.loads(request.data)
    print("Payment received!")
    print("Request Identifier: %s" % payment_payload.get("requestIdentifier"))
    print("Payment Method Dictionary: %s" % str(
        payment_payload.get("payment").get("paymentToken").get("paymentMethod")
    ))

    # this is where you will actually process the payment
    # for a minimum example here, we are approving any payments received
    # no actual payment is happening here
    payment_payload["status"] = "STATUS_SUCCESS"

    response = app.response_class(
        response=json.dumps(payment_payload),
        status=200,
        mimetype='application/json'
    )
    return response


app.run(host='0.0.0.0', port=8002)

# Expected output:
# Payment received!
# Request Identifier: <request identifier in message payload>
# Payment Method Dictionary: {'displayName': 'Visa 1234', 'type': 'Credit', 'network': 'Visa'}
