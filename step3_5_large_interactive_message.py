# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import base64
import gzip
import json
import jwt
import requests
import io

from attachment_cipher import decrypt, encrypt
from config import BIZ_ID, BUSINESS_CHAT_SERVER, CSP_ID, SECRET
from jwt_util import get_jwt_token

from flask import Flask, request, abort

app = Flask(__name__)


@app.route("/message", methods=['POST'])
def receive_large_interactive_payload():
    # here we are sending and receiving the interactive payload

    # Verify the authentication
    try:
        authorization = request.headers.get("Authorization")
    except TypeError as e:
        print("\nSYSTEM: jwt_token get error: %s" % e)
        abort(400)

    try:
        jwt_token = authorization[7:]    # <-- skip the Bearer prefix
    except TypeError as etype:
        print("\nSYSTEM: jwt_token authorization error: %s" % etype)
        abort(400)

    try:
        jwt.decode(jwt=jwt_token,
                   key=base64.b64decode(SECRET),
                   audience=CSP_ID)
    except Exception as e:
        print("\nSYSTEM: Authorization failed, error message: %s" % e)
        abort(403)

    # read the Gzip data
    fileobj = io.StringIO(request.data)
    uncompressed = gzip.GzipFile(fileobj=fileobj, mode='rb')
    try:
        payj = uncompressed.read()
    except IOError as eio:
        print("\nSYSTEM: Payload decompression error: %s" % eio)
        abort(400)

    # decode JSON
    try:
        payload = json.loads(payj)
    except ValueError as eve:
        print("\nSYSTEM: Payload decode error: %s" % eve)
        abort(400)

    print("payload %s" % payload)
    message_type = payload.get("type")
    if message_type != "interactive":
        print("Received a %s instead of an interactive ..." % message_type)
    else:
        jdataref = payload["interactiveDataRef"]

        attachment_file_name = "data_reference_debug.json"
        decryption_key = jdataref.get("key").upper()
        mmcs_url = jdataref.get("url")
        mmcs_owner = jdataref.get("owner")
        file_size = jdataref.get("size")
        bid = jdataref.get("bid")

        # get hex encoded signature and convert to base64
        hex_encoded_signature = jdataref.get("signature").upper()
        signature = base64.b16decode(hex_encoded_signature)
        base64_encoded_signature = base64.b64encode(signature)

        predownload_headers = {
            "Authorization": "Bearer %s" % get_jwt_token(),
            "source-id": BIZ_ID,
            "MMCS-Url": mmcs_url,
            "MMCS-Signature": base64_encoded_signature,
            "MMCS-Owner": mmcs_owner
        }

        r = requests.get("%s/preDownload" % BUSINESS_CHAT_SERVER,
                         headers=predownload_headers,
                         timeout=10)

        download_url = json.loads(r.content).get("download-url")

        # download the attachment data with GET request
        encrypted_attachment_data = requests.get(download_url).content

        # compare download size with expected file size
        if len(encrypted_attachment_data) != file_size:
            raise Exception("Data downloaded not of expected size! Check preDownload step.")

        # decrypted the downloaded data
        decrypted_attachment_data = decrypt(encrypted_attachment_data, decryption_key)

        decode_headers = {
            "Authorization": "Bearer %s" % get_jwt_token(),
            "source-id": BIZ_ID,
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "bid": bid
        }
        r = requests.post("%s/decodePayload" % BUSINESS_CHAT_SERVER,
                          headers=decode_headers,
                          data=decrypted_attachment_data,
                          timeout=10)

        # Write out the Business Chat server response
        print("%d: %s" % (r.status_code, r.text))

        # Write out the file
        print("\nSYSTEM: Writing full response to local file: %s" % attachment_file_name)
        with open(attachment_file_name, "wb") as attachment_local_file:
            attachment_local_file.write(r.text)

    return "ok"


app.run(host='0.0.0.0', port=8002)

# Expected output:
