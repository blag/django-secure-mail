import re
import sys

from django.core.management import call_command, CommandError
from django.test import TestCase

from secure_mail.models import Key

from tests.utils import TEST_KEY_FINGERPRINT

from io import StringIO


class TestEmailSigningKeyCommandTestCase(TestCase):
    def _generate_signing_key(self):
        out = StringIO()
        err = StringIO()

        self.assertEqual(Key.objects.count(), 0)

        call_command('email_signing_key', '--generate', '--passphrase', '""',
                     stdout=out, stderr=err)

        key_data = out.getvalue().strip().split('\n')

        fp, header, *blocks, footer = key_data

        self.assertRegex(fp, r'^[0-9A-F]{40}$')
        self.assertEqual(header, "-----BEGIN PGP PUBLIC KEY BLOCK-----")
        self.assertEqual(footer, "-----END PGP PUBLIC KEY BLOCK-----")

        self.assertEqual(err.getvalue(), '')

        self.assertEqual(Key.objects.count(), 1)

        key = Key.objects.get()

        key_data = [header, *blocks, footer]

        self.assertEqual(key.key.strip(), '\n'.join(key_data))

        self.fp = fp

    def _delete(self, key):
        for address in key.address_set.all():
            address.delete()

        key.delete()

        self.assertEqual(Key.objects.count(), 0)

    def test_generated_signing_key(self):
        self._generate_signing_key()

        self._delete(Key.objects.get())

    def test_print_private_key(self):
        self._generate_signing_key()

        print_out = StringIO()
        print_err = StringIO()

        call_command('email_signing_key', self.fp, '--print-private-key',
                     '--passphrase', '""',
                     stdout=print_out, stderr=print_err)

        print_private_key_data = print_out.getvalue().strip().split('\n')
        header, version, *_, footer = print_private_key_data

        # The "Version" header key is not required:
        # https://security.stackexchange.com/a/46609
        # self.assertRegex(version, r'^Version: .*$')
        self.assertEqual(header, "-----BEGIN PGP PRIVATE KEY BLOCK-----")
        self.assertEqual(footer, "-----END PGP PRIVATE KEY BLOCK-----")

        self.assertEqual(print_err.getvalue(), '')

        self.assertEqual(Key.objects.count(), 1)

        self._delete(Key.objects.get())

    def test_upload_to_keyservers(self):
        self._generate_signing_key()

        data = {
            'keyservers': [],
            'fingerprint': '',
        }

        def fake_upload_keys(keyservers, fingerprint):
            data['keyservers'] = keyservers
            data['fingerprint'] = fingerprint

        upload_out = StringIO()
        upload_err = StringIO()

        from secure_mail.management.commands import email_signing_key
        previous_value = email_signing_key.upload_keys
        email_signing_key.upload_keys = fake_upload_keys

        call_command('email_signing_key', self.fp, '--keyserver', 'localhost',
                     stdout=upload_out, stderr=upload_err)

        self.assertEqual(data['keyservers'], 'localhost')
        self.assertEqual(data['fingerprint'], self.fp)

        self.assertEqual(upload_out.getvalue(), '')
        self.assertEqual(upload_err.getvalue(), '')

        email_signing_key.upload_keys = previous_value

        self._delete(Key.objects.get())

    def test_fingerprint_and_generate_flag_raises_error(self):
        out = StringIO()
        err = StringIO()

        rgx = re.compile(r'^You cannot specify fingerprints and --generate '
                         r'when running this command$')

        self.assertEqual(Key.objects.count(), 0)

        with self.assertRaisesRegex(CommandError, rgx):
            call_command('email_signing_key', TEST_KEY_FINGERPRINT,
                         generate=True, stdout=out, stderr=err)

        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), '')

    def test_no_matching_fingerprint_raises_error(self):
        out = StringIO()
        err = StringIO()

        missing_fingerprint = '01234567890ABCDEF01234567890ABCDEF01234567'
        rgx = re.compile(r'''^Key matching fingerprint '{fp}' not '''
                         r'''found.$'''.format(fp=missing_fingerprint))

        self.assertEqual(Key.objects.count(), 0)

        with self.assertRaisesRegex(CommandError, rgx):
            call_command('email_signing_key', missing_fingerprint,
                         stdout=out, stderr=err)

        self.assertEqual(out.getvalue(), '')
        self.assertEqual(err.getvalue(), '')
