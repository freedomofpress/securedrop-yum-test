#!/usr/bin/env python3
"""
Clean up old packages, specifying how many to keep

Example:
    ./clean-old-packages securedrop-yum-test/workstation/buster-nightlies 7

This script is run in CI in a Fedora container. You can spin up a similar
container locally using podman or docker, e.g.:

    podman run -it --rm -v $(pwd):/workspace:Z fedora:39 bash

`rpmdev-vercmp` is provided by `rpmdevtools`.
"""
import argparse
import functools
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Tuple


def sort_rpm_versions(one: Tuple[str, Path], two: Tuple[str, Path]):
    """sort two RPM package versions"""
    status = subprocess.run(['rpmdev-vercmp', one[0], two[0]], stdout=subprocess.DEVNULL)
    if status.returncode == 11:
        # false, one is bigger
        return 1
    else:  # status.returncode == 12
        # true, two is bigger
        return -1


def rpm_info(path: Path) -> Tuple[str, str]:
    """
    Get RPM package name and version using a single subprocess call to rpm command.
    Returns a tuple of (name, version-release)
    """
    # n.b. we shell out to `rpm` because we can ignore the missing PGP key,
    # while using python3-rpm errors on it in a way that isn't recoverable.
    cmd = ['rpm', '-qp', '--qf', '%{NAME}|%{VERSION}-%{RELEASE}', str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    name, version_release = result.stdout.split('|')

    return name, version_release

def cleanup(data, to_keep: int, sorter):
    for name, versions in sorted(data.items()):
        if len(versions) <= to_keep:
            # Nothing to delete
            continue
        print(f'### {name}')
        items = sorted(versions.items(), key=functools.cmp_to_key(sorter), reverse=True)
        keeps = items[:to_keep]
        print('Keeping:')
        for _, keep in keeps:
            print(f'* {keep.name}')
        delete = items[to_keep:]
        print('Deleting:')
        for _, path in delete:
            print(f'* {path.name}')
            path.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="Cleans up old packages"
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory to clean up",
    )
    parser.add_argument(
        "keep",
        type=int,
        help="Number of packages to keep"
    )
    args = parser.parse_args()
    if not args.directory.is_dir():
        raise RuntimeError(f"Directory, {args.directory}, doesn't exist")
    print(f'Only keeping the latest {args.keep} packages')
    rpms = defaultdict(dict)
    for rpm in args.directory.glob('*.rpm'):
        name, version = rpm_info(rpm)
        rpms[name][version] = rpm

    cleanup(rpms, args.keep, sort_rpm_versions)


if __name__ == '__main__':
    main()
