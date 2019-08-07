# Copyright 2016-2018 Apple, Inc.
# All Rights Reserved.

import os
import base64
from Crypto.Cipher import AES
from Crypto.Util import Counter

import codecs

def encrypt(data):
    key = os.urandom(32)
    hexlify = codecs.getencoder('hex')

    decryption_key = "00%s" % base64.b16encode(key)

    iv = ""
    iv_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in iv_vector:
        iv += chr(i)
    ctr = Counter.new(128, initial_value=int(hexlify(iv.encode('utf-8'))[0], 16))
    # ctr = Counter.new(128, initial_value=int(iv.encode("hex"), 16))
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    encrypted_data = cipher.encrypt(data)

    return encrypted_data, decryption_key


def decrypt(encrypted_data, orig_key):
    key = base64.b16decode(orig_key[2:])

    iv = ""
    iv_vector = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in iv_vector:
        iv += chr(i)


    print('iv ==>',iv)
    hexlify = codecs.getencoder('hex')
    # ctr = Counter.new(128, initial_value=int(iv.encode("hex"), 16))
    ctr = Counter.new(128, initial_value=int(hexlify(iv.encode('utf-8'))[0], 16))
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    decrypted = cipher.decrypt(encrypted_data)

    return decrypted
