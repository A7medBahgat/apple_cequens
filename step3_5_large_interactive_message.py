# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import base64
import gzip
import json
import jwt
import requests
import io

from .attachment_cipher import decrypt, encrypt
from .config import BIZ_ID, BUSINESS_CHAT_SERVER, CSP_ID, SECRET
from .jwt_util import get_jwt_token

from flask import Flask, request, abort

app = Flask(__name__)


@app.route("/message", methods=['POST'])
def receive_large_interactive_payload(r=request):
    # here we are sending and receiving the interactive payload

    # Verify the authentication
    try:
        authorization = request.headers.get("Authorization")
        print ("beginning of authorization==> ")
        print(authorization)
        print("  ==>end of authorization");
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
    print(request.data)
    fileobj = io.BytesIO (request.data)
    uncompressed = gzip.GzipFile(fileobj=fileobj, mode='rb')

    try:
        payj = uncompressed.read()
        print(payj)
    except IOError as eio:
        print("\nSYSTEM: Payload decompression error: %s" % eio)
        abort(400)

    # decode JSON
    try:
        print("request arg ==> ")
        print(json.dumps(request.form.to_dict()))
        payload  = json.loads(json.dumps(request.form.to_dict()))
        # payload = json.dump(payload, StringIO('["streaming API"]'))

        print(type(payload))
    except ValueError as eve:
        print("\nSYSTEM: Payload decode error: %s" % eve)
        abort(400)

    print("payload %s" % payload)
    message_type = payload.get("type")
    print(message_type);
    if message_type != "interactive":
        print("Received a %s instead of an interactive ..." % message_type)
    else:
        jdataref = payload["interactiveDataRef[url]"]

        attachment_file_name = "data_reference_debug.json"
        decryption_key = payload["interactiveDataRef[key]"].upper()
        mmcs_url = payload["interactiveDataRef[url]"]
        mmcs_owner = payload["interactiveDataRef[owner]"]
        file_size = payload["interactiveDataRef[size]"]
        bid = payload["interactiveDataRef[bid]"]

        # get hex encoded signature and convert to base64
        hex_encoded_signature = payload["interactiveDataRef[signature]"].upper()
        signature = base64.b16decode(hex_encoded_signature)
        base64_encoded_signature = base64.b64encode(signature)

        predownload_headers = {
            "Authorization": "Bearer %s" % get_jwt_token(),
            "source-id": BIZ_ID,
            "MMCS-Url": mmcs_url,
            "MMCS-Signature": base64_encoded_signature,
            "MMCS-Owner": mmcs_owner
        }
        print("pre download headers ==>")
        print(predownload_headers)
        print(BUSINESS_CHAT_SERVER)
        r = requests.get("%s/preDownload" % BUSINESS_CHAT_SERVER,
                         headers=predownload_headers,
                         timeout=10)
        print(r.status_code)
        print(r.content);
        download_url = json.loads(r.content.decode('utf-8')).get("download-url")
        # download_url = json.loads(r.content.decode('utf-8')).get("download-url");
        print(download_url)
        # download the attachment data with GET request
        encrypted_attachment_data = requests.get(download_url).content
        print("size :: ")
        print(file_size)
        print("retrieved size ")
        print(len(encrypted_attachment_data))
        # compare download size with expected file size
        # if len(encrypted_attachment_data) != file_size:
            # raise Exception("Data downloaded not of expected size! Check preDownload step.")

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
            attachment_local_file.write((r.text).decode('utf-8'))

    return r.text


app.run(host='127.0.0.1', port=8002)

# Expected output:
