from django.test import TestCase

from secure_mail.models import Address, Key

from tests.utils import (
    TEST_KEY_FINGERPRINT, TEST_PUBLIC_KEY, DeleteAllKeysMixin,
)


class ModelFunctionTestCase(DeleteAllKeysMixin, TestCase):
    # This isn't too complex yet, but there are a few things left to do:
    #
    # * Implement queryset functions (create, update, delete)
    # * Implement tests for queryset functions
    # * Refactor functionality in the models' .save() function into signal
    #   handlers and connect them up in secure_mail/apps.py
    #
    # Once we implement that this will get "filled in" a bit more
    #
    def test_key_model_functions(self):
        key = Key(key=TEST_PUBLIC_KEY, use_asc=False)
        key.save()

        # Test Key.__str__()
        self.assertEqual(str(key), TEST_KEY_FINGERPRINT)

        # Test Key.email_addresses property
        self.assertEqual(key.email_addresses,
                          'django-secure-mail@example.com')

        address = Address.objects.get(key=key)

        # Test Address.__str__()
        self.assertEqual(str(address), 'django-secure-mail@example.com')

        self.assertEqual(address.address, 'django-secure-mail@example.com')

        fp = key.fingerprint
        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        address.delete()
        key.delete()

        self.assertEqual(Address.objects.count(), 0)
        self.assertEqual(Key.objects.count(), 0)

    def test_address_delete_only_keys_matching_address(self):
        key = Key(key=TEST_PUBLIC_KEY, use_asc=False)
        key.save()

        from secure_mail.settings import SIGNING_KEY_DATA
        self.gpg.gen_key(self.gpg.gen_key_input(**SIGNING_KEY_DATA))

        # Test Key.__str__()
        self.assertEqual(str(key), TEST_KEY_FINGERPRINT)

        # Test Key.email_addresses property
        self.assertEqual(key.email_addresses,
                          'django-secure-mail@example.com')

        address = Address.objects.get(key=key)

        address.delete()
        key.delete()

        self.assertEqual(Address.objects.count(), 0)
        self.assertEqual(Key.objects.count(), 0)

        self.assertEqual(len(self.gpg.list_keys()), 1)

        self.delete_all_keys()

        self.assertEqual(len(self.gpg.list_keys()), 0)
