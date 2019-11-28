import os
import requests
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
    def test_installimage_config_file_has_default_config(self, hostname):
        expectOS = ('/root/.oldroot/nfs/images/'
                    'Ubuntu-1604-xenial-64-minimal.tar.gz')

        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/root/installimage.cfg')

        assert f.contains('SWRAID 0')
        assert f.contains('SWRAIDLEVEL 0')
        assert f.contains('DRIVE1')
        assert not f.contains('DRIVE2')

        assert f.contains(expectOS)

    @idata(host_generator())
    def test_hostcode_file_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/etc/hostcode')

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'

    @idata(host_generator())
    def test_temp_ssh_keyfile_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/root/tmpKey')

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'

    @idata(host_generator())
    def test_rescue_endpoint_posted(self, hostname):
        host_ip = get_ip(testinfra.get_host("docker://" + hostname))

        response = requests.get(self.hetzner_robot_base_url +
                                "/boot/" + host_ip + "/rescue",
                                auth=self.auth)

        host_ip_parts = host_ip.split('.')
        self.assertEqual(len(host_ip_parts), 4)

        self.assertDictEqual(response.json(), {
            'rescue': {
                'active': False,  # active does not change in mock server
                'arch': '64',
                'authorized_key':
                    'fi:ng:er:pr:in:t0:00:00:00:00:00:00:00:00:00:00',
                'host_key': [],
                'os': 'linux',  # os choosen during playbook run
                'password': '',
                'server_ip': host_ip,
                'server_number': host_ip_parts[3]}
            }
        )

    @idata(host_generator())
    def test_reset_endoint_posted(self, hostname):
        host_ip = get_ip(testinfra.get_host("docker://" + hostname))

        response = requests.get(self.hetzner_robot_base_url +
                                "/reset/" + host_ip,
                                auth=self.auth)

        host_ip_parts = host_ip.split('.')
        self.assertEqual(len(host_ip_parts), 4)

        self.assertDictEqual(response.json(), {
            'reset': {
                'server_ip': host_ip,
                'server_number': host_ip_parts[3],
                'type': 'hw',  # type choosen during playbook run
                'operating_status': 'not supported'}
            }
        )

    @idata(host_generator())
    def test_server_name_posted(self, hostname):
        host_ip = get_ip(testinfra.get_host("docker://" + hostname))

        response = requests.get(self.hetzner_robot_base_url +
                                "/server/" + host_ip,
                                auth=self.auth)

        host_ip_parts = host_ip.split('.')
        self.assertEqual(len(host_ip_parts), 4)

        self.assertDictEqual(response.json(), {
            'server': {
                'cancelled': False,
                'dc': 'NBG1-DC1',
                'flatrate': True,
                'ip': [host_ip],
                'paid_until': '2010-09-02',
                'product': 'DS 3000',
                'server_ip': host_ip,
                'server_name': hostname,
                'server_number': host_ip_parts[3],
                'status': 'ready',
                'subnet': [{'ip': '2a01:4f8:111:4221::', 'mask': '64'}],
                'throttled': True,
                'traffic': '5 TB'}
            }
        )


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
