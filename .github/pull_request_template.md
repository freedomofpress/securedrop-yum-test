###
Name of package:


### Test plan

- [ ] Tag in securedrop-workstation repository is correct: https://github.com/freedomofpress/securedrop-workstation/releases/tag/x.y.z
- [ ] Build logs are included: https://github.com/freedomofpress/build-logs/commit/1234
- [ ] CI is passing, the rpm is properly signed with the test key
- [ ] Unsigned RPM after running `rpm --delsign` on the signed RPM results in the checksum found in the build logs
