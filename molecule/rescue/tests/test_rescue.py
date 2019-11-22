import os
import requests
import unittest

from requests.auth import HTTPBasicAuth
import testinfra.utils.ansible_runner


class RescueModeTest(unittest.TestCase):
    hetzner_robot_base_url = os.getenv(
        'HETZNER_ROBOT_BASE_URL', 'http://localhost:3000'
    )
    auth = HTTPBasicAuth('robot', 'secret')

    def setUp(self):
        self.testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
            os.environ['MOLECULE_INVENTORY_FILE']
        ).get_hosts('all')

    def test_rescue_service_posted_for_infra_hosts(self):
        for hostname in self.testinfra_hosts:
            host_ip = get_ip(testinfra.get_host("docker://" + hostname))

            response = requests.get(self.hetzner_robot_base_url +
                                    "/boot/" + host_ip + "/rescue",
                                    auth=self.auth)

            host_ip_parts = host_ip.split('.')
            self.assertEqual(len(host_ip_parts), 4)

            self.assertDictEqual(response.json(), {
                'rescue': {
                    'active': False,
                    'arch': '64',
                    'authorized_key':
                        'fi:ng:er:pr:in:t0:00:00:00:00:00:00:00:00:00:00',
                    'host_key': [],
                    'os': 'linux',
                    'password': '',
                    'server_ip': host_ip,
                    'server_number': host_ip_parts[3]}
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
