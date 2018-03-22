from django.test import TestCase, override_settings


class GetGPGTestCase(TestCase):
    def test_get_gpg_default_encoding(self):
        from secure_mail import utils
        previous_value = utils.GNUPG_ENCODING
        try:
            utils.GNUPG_ENCODING = None
            gpg_obj = utils.get_gpg()
        finally:
            utils.GNUPG_ENCODING = previous_value

        # GPG.encoding is hard-coded to latin-1 in gnupg.py
        self.assertEquals(gpg_obj.encoding, 'latin-1')

    def test_get_gpg_specified_encoding(self):
        from secure_mail import utils
        previous_value = utils.GNUPG_ENCODING
        try:
            utils.GNUPG_ENCODING = 'utf-8'
            gpg_obj = utils.get_gpg()
        finally:
            utils.GNUPG_ENCODING = previous_value

        self.assertEquals(gpg_obj.encoding, 'utf-8')
