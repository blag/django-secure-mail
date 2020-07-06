import sys

from django.core.management import call_command
from django.core.management.base import SystemCheckError
from django.test import TestCase, override_settings

from secure_mail.checks import check_signing_key

from tests.utils import (
    GPGMixin, TEST_PRIVATE_KEY, TEST_KEY_FINGERPRINT,
)

from io import StringIO


MODIFIED_FINGERPRINT = "{}{}".format(
    TEST_KEY_FINGERPRINT[:-1],
    "0" if TEST_KEY_FINGERPRINT[-1] != "0" else "1")


@override_settings(
    SECURE_MAIL_SIGNING_KEY_FINGERPRINT=None)
class NoSigningKeyErrorTestCase(GPGMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'secure_mail.utils.send_mail'

    def test_check_signing_key(self):
        self.assertEqual(check_signing_key([]), [])


@override_settings(
    SECURE_MAIL_SIGNING_KEY_FINGERPRINT=TEST_KEY_FINGERPRINT)
class NoBadSigningKeyErrorTestCase(GPGMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'secure_mail.utils.send_mail'

    def setUp(self):
        super(NoBadSigningKeyErrorTestCase, self).setUp()
        self.gpg.import_keys(TEST_PRIVATE_KEY)

    def tearDown(self):
        super(NoBadSigningKeyErrorTestCase, self).tearDown()
        self.gpg.delete_keys(TEST_KEY_FINGERPRINT, secret=True,
                             passphrase='')
        self.gpg.delete_keys(TEST_KEY_FINGERPRINT)

    def test_successful_check(self):
        from secure_mail import (checks, settings, utils)
        try:
            previous_utils_value = utils.SIGNING_KEY_FINGERPRINT
            utils.SIGNING_KEY_FINGERPRINT = TEST_KEY_FINGERPRINT

            previous_settings_value = settings.SIGNING_KEY_FINGERPRINT
            settings.SIGNING_KEY_FINGERPRINT = TEST_KEY_FINGERPRINT

            previous_checks_value = checks.SIGNING_KEY_FINGERPRINT
            checks.SIGNING_KEY_FINGERPRINT = TEST_KEY_FINGERPRINT

            fout = StringIO()
            ferr = StringIO()
            call_command('check', 'secure_mail', stdout=fout, stderr=ferr)
        finally:
            checks.SIGNING_KEY_FINGERPRINT = previous_checks_value
            settings.SIGNING_KEY_FINGERPRINT = previous_settings_value
            utils.SIGNING_KEY_FINGERPRINT = previous_utils_value


@override_settings(
    SECURE_MAIL_SIGNING_KEY_FINGERPRINT=MODIFIED_FINGERPRINT)
class BadSigningKeyErrorTestCase(GPGMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'secure_mail.utils.send_mail'

    def setUp(self):
        super(BadSigningKeyErrorTestCase, self).setUp()
        self.gpg.import_keys(TEST_PRIVATE_KEY)

    def tearDown(self):
        super(BadSigningKeyErrorTestCase, self).tearDown()
        self.gpg.delete_keys(TEST_KEY_FINGERPRINT, secret=True,
                             passphrase='')
        self.gpg.delete_keys(TEST_KEY_FINGERPRINT)

    def test_unsuccessful_check(self):
        from secure_mail import (checks, settings, utils)
        try:
            previous_utils_value = utils.SIGNING_KEY_FINGERPRINT
            utils.SIGNING_KEY_FINGERPRINT = MODIFIED_FINGERPRINT

            previous_settings_value = settings.SIGNING_KEY_FINGERPRINT
            settings.SIGNING_KEY_FINGERPRINT = MODIFIED_FINGERPRINT

            previous_checks_value = checks.SIGNING_KEY_FINGERPRINT
            checks.SIGNING_KEY_FINGERPRINT = MODIFIED_FINGERPRINT

            fout = StringIO()
            ferr = StringIO()
            with self.assertRaises(SystemCheckError):
                call_command('check', 'secure_mail', stdout=fout, stderr=ferr)
        finally:
            checks.SIGNING_KEY_FINGERPRINT = previous_checks_value
            settings.SIGNING_KEY_FINGERPRINT = previous_settings_value
            utils.SIGNING_KEY_FINGERPRINT = previous_utils_value
