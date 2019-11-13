import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_autosetupfile_exists(host):
    f = host.file('/autosetup')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_autosetupfile_has_correct_config(host):
    f = host.file('/autosetup')

    assert f.contains('SWRAID 1')
    assert f.contains('SWRAIDLEVEL 1')
    assert f.contains('DRIVE1')
    assert f.contains('DRIVE2')

    assert not f.contains('Ubuntu-1604-xenial-64-minimal')
    assert f.contains('Debian-101-buster-64-minimal')
