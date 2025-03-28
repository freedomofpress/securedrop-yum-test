#!/usr/bin/env python3
"""
Script for generating yum repository metadata in a reproducible manner.

Files are copied into public/ and metadata is generated there. All RPMs
have their mtime fixed to a specific timestamp, so the generated XML/SQLite
files will be reproducible.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import xml.etree.ElementTree as ET


def fetch_reproduce_timestamp(public: Path) -> int:
    repomd = next(public.glob("workstation/dom0/*/repodata/repomd.xml"))
    tree = ET.parse(repomd)
    root = tree.getroot()
    revision = root.find(
        "repo:revision", {"repo": "http://linux.duke.edu/metadata/repo"}
    )
    print(f"Will use a timestamp of {revision.text} (from {repomd})")
    return int(revision.text)


def main():
    root = Path(__file__).parent.parent.parent
    public = root / "public"
    workstation = root / "workstation"
    if "--reproduce" in sys.argv:
        try:
            timestamp = fetch_reproduce_timestamp(public)
        except Exception as err:
            raise RuntimeError("Failed to fetch timestamp from repomd.xml") from err
    else:
        # Use the current time
        timestamp = int(time.time())
    # Reset public, copy the workstation/ tree into it
    print("Creating public/ (from scratch)")
    if public.exists():
        shutil.rmtree(public)
    public.mkdir()
    shutil.copytree(workstation, public / "workstation")
    for rpm in public.glob("**/*.rpm"):
        os.utime(rpm, (timestamp, timestamp))
    # Folders are public/workstation/dom0/fXX, run createrepo_c in each one
    for folder in public.glob("*/*/*/"):
        if not folder.is_dir():
            continue
        print(f"Generating metadata for {folder}")
        # The <revision> and <timestamp> fields are set to the current UNIX time
        # unless we explicitly override them. Use our fixed time to ensure it's
        # consistent regardless of how long this command takes to run.
        subprocess.check_call(
            [
                "createrepo_c",
                "--revision",
                str(timestamp),
                "--set-timestamp-to-revision",
                str(folder),
            ]
        )
    print("Done!")


if __name__ == "__main__":
    main()
