import os
import unittest

import testinfra.utils.ansible_runner
from ddt import ddt, idata

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def host_generator():
    for hostname in testinfra_hosts:
        yield hostname


@ddt
class RescueModeTest(unittest.TestCase):

    @idata(host_generator())
    def test_installimage_config_file_not_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/root/installimage.cfg')

        assert not f.exists

    @idata(host_generator())
    def test_provisioned_flag_file_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/etc/hetzner_installimage_provisioned.flag')

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'


def get_ip(host):
    get_ip_run = host.run("python -c 'import socket; print([" +
                          "l for l in ([ip for ip in socket." +
                          "gethostbyname_ex(socket." +
                          "gethostname())[2] if not ip.startswith" +
                          "(\"127.\")][:1], [[(" +
                          "s.connect((\"8.8.8.8\", 53)), " +
                          "s.getsockname()[0], s.close()) " +
                          "for s in [socket.socket" +
                          "(socket.AF_INET, socket.SOCK_DGRAM)]]" +
                          "[0][1]]) if l][0][0])'")

    ip = get_ip_run.stdout.strip()
    return ip
