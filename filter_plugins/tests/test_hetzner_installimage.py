import unittest

from filter_plugins.hetzner_installimage import *


class HetznerInstallimageTest(unittest.TestCase):

    def test_init(self):
        module = FilterModule()
        filters = module.filters()

        self.assertEqual(filters.get('hetzner_installimage_form_urlencode'), form_urlencode.form_urlencode)
