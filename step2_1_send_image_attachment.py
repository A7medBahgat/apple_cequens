# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import base64
import requests
import uuid

from .attachment_cipher import encrypt
from .config import BIZ_ID, BUSINESS_CHAT_SERVER
from .jwt_util import get_jwt_token
from flask import Flask, request, abort

UNICODE_OBJ_REPLACEMENT_CHARACTER = "\uFFFC"


@app.route("/sendattachment", methods=['POST'])
def send_message_with_image_attachment(destination_id = request.destination_id,
image_file_path=request.image_file_path):
    # load image data

    with open(image_file_path, "rb") as image_file:
        image_data = image_file.read()

    # encrypt image data, and retrieve key for decryption
    encrypted_data, decryption_key = encrypt(image_data)

    # do pre-upload to get upload-url
    pre_upload_headers = {
        "Authorization": "Bearer %s" % get_jwt_token(),
        "Source-Id": BIZ_ID,
        "MMCS-Size": str(len(encrypted_data))
    }

    r = requests.get("%s/preUpload" % BUSINESS_CHAT_SERVER,
                     headers=pre_upload_headers,
                     timeout=10)

    upload_url = r.json().get("upload-url")
    mmcs_url = r.json().get("mmcs-url")
    mmcs_owner = r.json().get("mmcs-owner")

    upload_headers = {
        "content-length": str(len(encrypted_data))
    }

    # upload encrypted image data
    r = requests.post(upload_url,
                      data=encrypted_data,
                      headers=upload_headers,
                      timeout=10)

    if r.status_code != 200:
        raise Exception("Image attachment upload failed!")

    # convert file signature from base-64-encoded to hex-encoded
    base64_encoded_signature = r.json().get("singleFile").get("fileChecksum")
    signature = base64.b64decode(base64_encoded_signature)
    hex_encoded_signature = base64.b16encode(signature)

    message_id = str(uuid.uuid4())  # generate unique message id

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % get_jwt_token(),
        "id": message_id,
        "Source-Id": BIZ_ID,
        "Destination-Id": destination_id
    }

    size_in_bytes = str(len(encrypted_data))  # has to be of type string

    payload = {
        "id": message_id,
        "type": "text",
        "sourceId": BIZ_ID,
        "destinationId": destination_id,
        "v": 1,
        "body": "Here's the attachment: %s" % UNICODE_OBJ_REPLACEMENT_CHARACTER,
        "attachments": [{
            "name": "image_filename.jpg",
            "mime-type": "image/jpeg",
            "file-size": size_in_bytes,
            "mmcs-signature-hex": hex_encoded_signature,
            "mmcs-url": mmcs_url,
            "mmcs-owner": mmcs_owner,
            "decryption-key": decryption_key
        }]
    }

    r = requests.post("%s/message" % BUSINESS_CHAT_SERVER,
                      json=payload,
                      headers=headers,
                      timeout=10)

    print("Business Chat server return code: %s" % r.status_code)


if __name__ == "__main__":
    destination_id = "<source_id from previously received message>"
    image_file_path = "<path to image file>"

    send_message_with_image_attachment(destination_id, image_file_path)

# Expected output:
# Business Chat server return code: 200
