#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import json

PROD_SIGNING_KEY_PATH = "pubkeys/prod.key"
DEV_SIGNING_KEY_PATH = "pubkeys/test.key"
RPM_DIR = "workstation"


def verify_sig_rpm(path, dev=False):

    key_path = ""
    if dev:
        key_path = DEV_SIGNING_KEY_PATH
    else:
        key_path = PROD_SIGNING_KEY_PATH
    try:
        subprocess.check_call(["rpmkeys", "--import", key_path])
    except subprocess.CalledProcessError as e:
        fail("Error importing key: {}".format(str(e)))

    # Check the signature
    try:
        output = subprocess.check_output(["rpm", "--checksig", path])
        # rpm --checksig returns 0 if there is *no* signature. I couldn't
        # find a way other than parsing stdout
        line = output.decode("utf-8").rstrip()
        print(line)
        expected_output = "{}: digests signatures OK".format(path)
        if line != expected_output:
            fail("Signture verification failed for {}:{}".format(expected_output, line))
    except subprocess.CalledProcessError as e:
        fail("Error checking signature: {}".format(str(e)))


def verify_all_rpms(dev=False):
    for root, dirs, files in os.walk(RPM_DIR):
        for name in files:
            verify_sig_rpm(os.path.join(root, name), dev)


def remove_keys_in_rpm_keyring():
    rpm_keys_exist = False
    try:
        # Returns non-zero if no keys are installed
        subprocess.check_call(["rpm", "-q", "gpg-pubkey"])
        rpm_keys_exist = True
    except subprocess.CalledProcessError:
        rpm_keys_exist = False

    # If a key is in the keyring, delete it
    if rpm_keys_exist:
        try:
            subprocess.check_call(["rpm", "--erase", "--allmatches", "gpg-pubkey"])
        except subprocess.CalledProcessError as e:
            fail("Failed to delete key: {}".format(str(e)))


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", action="store_true", default=False)
    parser.add_argument("--verify", action="store_true", default=True)
    parser.add_argument("--all", action="store_true", default=False)
    parser.add_argument("packages", type=str, nargs="*", help="Files to sign/verify")
    args = parser.parse_args()

    # Fail if no package is specified or not using '--all'
    if not args.all and not args.packages:
        fail("Please specify a rpm package or --all")
    # Since we can't specify with which key to check sigs, we should clear the keyring
    remove_keys_in_rpm_keyring()

    if args.verify:
        if args.all:
            verify_all_rpms(args.dev)
        else:
            for package in args.packages:
                assert os.path.exists(package)
                verify_sig_rpm(package, args.dev)

    sys.exit(0)


if __name__ == "__main__":
    main()
