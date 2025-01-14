"""
commandline interface code.
"""

from __future__ import print_function

import argparse
from binascii import hexlify, unhexlify
import sys

from aestools.checkkey import is_key_safe, selftest, THRESHOLD_DEFAULT, bit_strength_gcm_auth, bit_strength_auth_key
from aestools.safekey import get_safe_key


def valid_key(s):
    """validator for key argument"""
    try:
        value = unhexlify(s.encode('ascii'))
    except:
        msg = "%r is not a valid key in hex representation" % s
        raise argparse.ArgumentTypeError(msg)
    if len(value) not in (16, 32):
        msg = "%r has a invalid key length" % s
        raise argparse.ArgumentTypeError(msg)
    if not isinstance(value, bytes):
        msg = "we did not get a byte value"
        raise argparse.ArgumentTypeError(msg)
    return value


def valid_bits(s):
    """validator for bits argument"""
    if s not in ('128', '256'):
        msg = "invalid key length, must be 128 or 256"
        raise argparse.ArgumentTypeError(msg)
    return int(s)


def main():
    def valid_threshold(value):
        value = int(value)
        if 0 < value <= 128:
            return value
        raise argparse.ArgumentTypeError('%i is not a valid threshold (must be between 1 and 128)')

    parser = argparse.ArgumentParser(description='AES tools')
    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')
    parser_check = subparsers.add_parser('check', help='check an AES GCM key')
    parser_check.add_argument('key', type=valid_key,
                              help='key in hex representation')
    parser_check.add_argument('--threshold', dest='threshold', type=valid_threshold,
                              default=THRESHOLD_DEFAULT, help='safety threshold')
    parser_check = subparsers.add_parser('hcheck', help='check a GCM Hash key')
    parser_check.add_argument('key', type=valid_key,
                              help='key in hex representation')
    parser_check.add_argument('--threshold', dest='threshold', type=valid_threshold,
                              default=THRESHOLD_DEFAULT, help='safety threshold')
    parser_generate = subparsers.add_parser('generate', help='generate a safe AES GCM key')
    parser_generate.add_argument('bits', type=valid_bits,
                                 help='key length, 128 or 256')
    args = parser.parse_args()

    if args.cmd == 'check':
        selftest()
        strength = bit_strength_gcm_auth(args.key)
        safe = strength >= args.threshold
        print("%s is safe: %r (%i bits security)" % (hexlify(args.key).decode('ascii'), safe, strength))
        return 0 if safe else 1

    if args.cmd == 'hcheck':
        selftest()
        strength = bit_strength_auth_key(args.key)
        safe = strength >= args.threshold
        if (safe):
            print("%s is safe: %r (%i bits security)" % (hexlify(args.key).decode('ascii'), safe, strength))
        else:
            print("%s is *NOT* safe: %r (%i bits security)" % (hexlify(args.key).decode('ascii'), safe, strength))
        return 0 if safe else 1

    if args.cmd == 'generate':
        selftest()
        key = get_safe_key(args.bits)
        print(hexlify(key).decode('ascii'))
        return 0


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
