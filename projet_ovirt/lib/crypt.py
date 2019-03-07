#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode, b64decode


def encode(string, encoding='utf-8'):
    return b64encode(bytes(string, encoding)).decode(encoding)


def decode(string, encoding='utf-8'):
    return b64decode(string).decode(encoding)


if __name__ == '__main__':
    import getpass
    import sys

    if len(sys.argv) == 2:
        if sys.argv[1] == 'encode':
            print('Entrer le mot de passe à crypter: ', end='', flush=True)
        else:
            print('Entrer la chaine à décrypter: ', end='', flush=True)
        s = getpass.getpass('')
    else:
        s = sys.argv[2]

    if sys.argv[1] == 'encode':
        print('Chaine cryptée (entre []): [{}]'.format(encode(s)))
    else:
        print('Chaine décryptée (entre []): [{}]'.format(decode(s)))
