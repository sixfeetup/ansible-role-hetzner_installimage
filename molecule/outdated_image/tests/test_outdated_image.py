import os
import unittest

from requests.auth import HTTPBasicAuth
from ddt import ddt, idata
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def host_generator():
    for hostname in testinfra_hosts:
        yield hostname


@ddt
class RescueModeTest(unittest.TestCase):
    hetzner_robot_base_url = os.getenv(
        'HETZNER_ROBOT_BASE_URL', 'http://localhost:3000'
    )
    auth = HTTPBasicAuth('robot', 'secret')

    @idata(host_generator())
    def test_installimage_config_file_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/root/installimage.cfg')

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'

    @idata(host_generator())
    def test_installimage_config_file_has_old_image_config(self, hostname):
        expectOS = ('/root/.oldroot/nfs/images.old/'
                    'Debian-102-buster-64-minimal.tar.gz')

        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/root/installimage.cfg')

        assert f.contains('SWRAID 0')
        assert f.contains('SWRAIDLEVEL 0')
        assert f.contains('DRIVE1')
        assert not f.contains('DRIVE2')

        assert f.contains(expectOS)
