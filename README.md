> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

# securedrop-workstation-dev-rpm-packages-lfs

Repository for storing nightly builds of [SecureDrop Workstation](https://github.com/freedomofpress/securedrop-workstation)
packages for continuous delivery to developer workstations. The packages here are RPMs, intended for installation
in `dom0` within [QubesOS](https://qubesos.org/)

## git-lfs

The repository requires use of [git-lfs](https://git-lfs.github.com/) to store large files.

## Publishing packages

Merging into the `main` branch will automatically deploy packages to
https://yum-test.securedrop.org/. Publishing happens every 15m.
test
