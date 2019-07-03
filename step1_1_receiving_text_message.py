# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import json
import gzip
import io
from flask import Flask, request

app = Flask(__name__)


@app.route("/message", methods=['POST'])
def receive_message():
    # read the Gzip data
    fileobj = io.StringIO(request.data)
    uncompressed = gzip.GzipFile(fileobj=fileobj, mode='rb')
    payload = json.loads(uncompressed.read())

    # possible types:
    # text, interactive, typing_start, typing_end, close
    message_type = payload.get("type")

    if message_type == "typing_start":
        print("User is typing...")

    elif message_type == "text":
        print("Just received a text message!")
        print("Message body: %s" % payload.get("body"))
        print("Source ID: %s" % request.headers.get("source-id"))
        print("Device Agent: %s" % request.headers.get("device-agent"))

    else:
        print("Received unknown type from user: %s" % message_type)

    return "ok"


app.run(host='0.0.0.0', port=8002)

# Expected output:
# User is typing...
# Just received a text message!
# Message body: Nice to meet you
# Source ID: urn:mbid:AQAAY8rFCwBeMO4UWPddFNdjT/1jwwWrsqVzupedIwUcd1/UIeBtgEHtnaqp1IbFCYyxxP+gYhMu9hICI48/Yzbffw+prP6fsYSMS/9vztCGNElhP/jGKpmlHAc5T/mTzAvGEjOfI9bsZJjurWPMZ7Emi0HuMUs=
