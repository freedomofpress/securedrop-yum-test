#!/usr/bin/env python3
"""
Autosign all RPM files

Usage: ./autosign.py <directory> --fingerprint <fingerprint>
"""

import argparse
import subprocess
from pathlib import Path


def is_unsigned(rpm: Path) -> bool:
    """
    Check if `rpm -Kv` includes "Header V4 RSA/SHA256 Signature", regardless of exit code
    """
    output = subprocess.run(
        ["rpm", "-Kv", str(rpm)], text=True, capture_output=True
    ).stdout
    return "Header V4 RSA/SHA256 Signature" not in output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Input directory")
    parser.add_argument(
        "--fingerprint", type=str, required=True, help="PGP fingerprint"
    )
    args = parser.parse_args()

    rpmmacros = Path("~/.rpmmacros").expanduser()
    if rpmmacros.exists():
        raise RuntimeError("RPM macros file already exists; don't want to clobber it")

    rpmmacros.write_text(f"%_gpg_name {args.fingerprint}\n")

    if not args.input.exists():
        raise RuntimeError(f"Input directory, {args.input}, does not exist")

    for rpm in args.input.glob("**/*.rpm"):
        if is_unsigned(rpm):
            print(f"Signing {rpm}")
            subprocess.check_call(["rpm", "--resign", str(rpm)])
        else:
            print(f"{rpm} is already signed")


if __name__ == "__main__":
    main()
