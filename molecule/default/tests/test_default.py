import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_autosetupfile_exists(host):
    f = host.file('/root/installimage.cfg')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_autosetupfile_has_correct_config(host):
    expectOS = '/root/.oldroot/nfs/images/Ubuntu-1604-xenial-64-minimal.tar.gz'
    f = host.file('/root/installimage.cfg')

    assert f.contains('SWRAID 0')
    assert f.contains('SWRAIDLEVEL 0')
    assert f.contains('DRIVE1')
    assert not f.contains('DRIVE2')

    assert f.contains(expectOS)
