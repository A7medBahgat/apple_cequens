# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import base64
import time
import jwt

from config import CSP_ID, SECRET


def get_jwt_token():
    alg_headers = {"alg": "HS256"}
    claim_payload = {
        "iss": CSP_ID,
        "iat": int(time.time())  # unit: seconds
    }
    jwt_token = jwt.encode(claim_payload,
                           base64.b64decode(SECRET),
                           algorithm='HS256',
                           headers=alg_headers)
    print("jwt_token %" % jwt_token)
    return jwt_token

if __name__ == '__main__':
    print (get_jwt_token())
