from email.mime.base import MIMEBase
from importlib import import_module
from os.path import basename

from django.conf import settings
from django.core import mail
from django.utils.safestring import mark_safe

from secure_mail.models import Key
from secure_mail.settings import SIGNING_KEY_PASSPHRASE
from secure_mail.utils import get_gpg, EncryptionFailedError

# Generated with:
#
# key_data = {
#     'key_type': "RSA",
#     'key_length': 4096,
#     'name_real': 'django-secure-mail test project',
#     # 'name_comment': "Test address and key for django-secure-mail",
#     'name_email': 'django-secure-mail@example.com',
#     'expire_date': 0,
# }

# key = gpg.gen_key(gpg.gen_key_input(**key_data))
# public_fp = key.fingerprint
# private_key = gpg.export_keys(key.fingerprint, secret=True, armor=True)
# public_key = gpg.export_keys(key.fingerprint, armor=True)
# # gpg.delete_keys([private_fp], secret=True, passphrase=SIGNING_KEY_PASSPHRASE)
# gpg.delete_keys([public_fp])
# print('TEST_KEY_FINGERPRINT = f"{public_fp}"')
# print('TEST_PRIVATE_KEY = f"""\n{private_key}"""')
# print('TEST_PUBLIC_KEY = f"""\n{public_key}"""')
#
TEST_KEY_FINGERPRINT = "27011D34B2A200A3367C23C450CF2FB1F5C0624D"
TEST_PRIVATE_KEY = """
-----BEGIN PGP PRIVATE KEY BLOCK-----
Version: GnuPG/MacGPG2 v2

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
bmdvLXNlY3VyZS1tYWlsIHRlc3QgcHJvamVjdCA8ZGphbmdvLXNlY3VyZS1tYWls
QGV4YW1wbGUuY29tPokCOQQTAQgAIwUCWPVi9QIbLwcLCQgHAwIBBhUIAgkKCwQW
AgMBAh4BAheAAAoJEFDPL7H1wGJNa50QALUpLOG3yHSAo1YJgl8kwIkVkGvEQPgv
bNMjhPQSaURQiDezi2rqFNTgkE8LekLckY6/PZMx1rGOEz3odEGGqR7x+/V/5/Pv
sw7gbbdHvhm2oCoL0AQkZld3DGbuyJ7/aayah6hVPeZdEhQVXH6OyvWNy43wkVVM
YheF2t33rIyhknIxx92Q3k3hkhUPFlvr89YYYcv1UVUbViFh5dHn+J1MVkYRiJ9G
DGK0amfxuAbIK0CFLBop/Hky3GvPhBLtPq2eVSi6dCXZPW9elicGP8f4hbx1ncGO
e2Q9Kn69lkP3IZQEDighEH2qZzPW6XTvkjQl3aBHn19NXhmPYyvUCHvQJZVr4tJV
ULz05DTEB4uClcVa8RADALwD7212y94mqtFFXSOeRI+fIN2rcKcQMS5z6YDBedJG
/tyzUiUbLfigqpguQlg/KWH7Iy7M8Vn+OFbz5BdOog7ydRHuIUjUTB9VsorWSTDD
n/fiJnxOp3m2WgUMdAaMC0LTRyudTCenGCU7VOenFqrE0J619HMfiUFWVuefYF9E
ZbULOtaw8iIIyY9fXAV0/IJ1DZSgj9b1wV0fvFq+tUmGpJqVE/u28b4F59TzQuLV
L17PFZFT/6dWwHAtYEz1sBRkjLjz9lMvrJ+xyJN6RxcUly/2aXqoJYy9D2HV2Hwg
+dSC2qTY1iry
=ptD7
-----END PGP PRIVATE KEY BLOCK-----
"""
TEST_PUBLIC_KEY = """
-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG/MacGPG2 v2

mQINBFj1YvUBEADE4L7qDCQINSwwygbcUb2BH909zk9/Ih1wRGB7rxoWFDbba0B7
lDfscxPX7+z+sXUFEjf4+puD4VdBibvZK3gswed9YNUZ7vJDb21TAEfVrjteQYMu
Y7dctnaXzxJwmG/BKYHtVTr7ZlqVHuazs7Kbfv9NHDVr2cLz5drAQ/Y9TBQJd1kc
wEnJZ/04EnkjuYVLlL2uKV76lmBoFNFJs8ug2yZmdGY4UBEPlslpqsl3Io76s+N9
p5ylmmaILf6fzAblcw2gHF/VKQAuZlOD38e69vd9p7PbZVsMQvXMMQZxREK2yB53
f98WgOKAOUzq+1Yrt+u6OFbMtArgJQUq/b7vUkmC4047vIwrLaH/0vI9S16osrmW
39nIp4VXzB55N/pd3ynqY+HU4iqErV74Cv1cNqaiirMToE/1Iiro5hZ6gmHMHR0p
ghGrHlyNt7UaSdjHlhFnCq7Xr7Wbra7lZpXzG6HtDBgQT848g5jOb5bKOdenKMHo
JRg90KDNSFo0PLvV3qL788LDAPbUJ1WkXcykg9Jkgw19SCa830CXWaf2X6Jc3hsL
0A5hg+b2o3EQrnZgSNUouY8v6foaAI9I7tvlktm0mvtsNqgxqsA/JqsXiVwTf7xh
AAdkitZH1ufMZkoXDK28Mdd28nTvko4fo7K1jCPPrI1KjPxeQnO3M2wdxQARAQAB
tEBkamFuZ28tc2VjdXJlLW1haWwgdGVzdCBwcm9qZWN0IDxkamFuZ28tc2VjdXJl
LW1haWxAZXhhbXBsZS5jb20+iQI5BBMBCAAjBQJY9WL1AhsvBwsJCAcDAgEGFQgC
CQoLBBYCAwECHgECF4AACgkQUM8vsfXAYk1rnRAAtSks4bfIdICjVgmCXyTAiRWQ
a8RA+C9s0yOE9BJpRFCIN7OLauoU1OCQTwt6QtyRjr89kzHWsY4TPeh0QYapHvH7
9X/n8++zDuBtt0e+GbagKgvQBCRmV3cMZu7Inv9prJqHqFU95l0SFBVcfo7K9Y3L
jfCRVUxiF4Xa3fesjKGScjHH3ZDeTeGSFQ8WW+vz1hhhy/VRVRtWIWHl0ef4nUxW
RhGIn0YMYrRqZ/G4BsgrQIUsGin8eTLca8+EEu0+rZ5VKLp0Jdk9b16WJwY/x/iF
vHWdwY57ZD0qfr2WQ/chlAQOKCEQfapnM9bpdO+SNCXdoEefX01eGY9jK9QIe9Al
lWvi0lVQvPTkNMQHi4KVxVrxEAMAvAPvbXbL3iaq0UVdI55Ej58g3atwpxAxLnPp
gMF50kb+3LNSJRst+KCqmC5CWD8pYfsjLszxWf44VvPkF06iDvJ1Ee4hSNRMH1Wy
itZJMMOf9+ImfE6nebZaBQx0BowLQtNHK51MJ6cYJTtU56cWqsTQnrX0cx+JQVZW
559gX0RltQs61rDyIgjJj19cBXT8gnUNlKCP1vXBXR+8Wr61SYakmpUT+7bxvgXn
1PNC4tUvXs8VkVP/p1bAcC1gTPWwFGSMuPP2Uy+sn7HIk3pHFxSXL/ZpeqgljL0P
YdXYfCD51ILapNjWKvI=
=Tb82
-----END PGP PUBLIC KEY BLOCK-----
"""


def send_mail_with_backend(
        subject, body, from_email, recipient_list, html_message=None,
        fail_silently=False, auth_user=None, auth_password=None,
        attachments=None, alternatives=None, connection=None, headers=None,
        do_not_encrypt_this_message=False):
    connection = connection or mail.get_connection(
        username=auth_user, password=auth_password,
        fail_silently=fail_silently,
    )
    message = mail.EmailMultiAlternatives(
        subject, body, from_email, recipient_list, attachments=attachments,
        connection=connection, headers=headers)

    if html_message:
        message.attach_alternative(html_message, 'text/html')

    for alternative, mimetype in alternatives or []:
        message.attach_alternative(alternative, mimetype)

    if do_not_encrypt_this_message:
        message.do_not_encrypt_this_message = True

    return message.send()


class GPGMixin(object):
    @classmethod
    def setUpClass(cls):
        cls.gpg = get_gpg()
        super(GPGMixin, cls).setUpClass()


class KeyMixin(GPGMixin):
    @classmethod
    def setUpClass(cls):
        super(KeyMixin, cls).setUpClass()
        # Import the public key through the Key model
        cls.key = Key.objects.create(key=TEST_PUBLIC_KEY,
                                     use_asc=cls.use_asc)
        cls.address = cls.key.address_set.first()

    @classmethod
    def tearDownClass(cls):
        for address in cls.key.address_set.all():
            address.delete()
        cls.key.delete()
        super(KeyMixin, cls).tearDownClass()


class DeleteAllKeysMixin(GPGMixin):
    def delete_all_keys(self):
        self.gpg.delete_keys([k['fingerprint'] for k in self.gpg.list_keys()],
                             secret=True, passphrase=SIGNING_KEY_PASSPHRASE)
        self.gpg.delete_keys([k['fingerprint'] for k in self.gpg.list_keys()])


class SendMailFunctionMixin(GPGMixin):
    send_mail_function = None

    def send_mail(self, *args, **kwargs):
        # if hasattr(self.send_mail_function, '__call__'):
        #     # Allow functions assigned directly
        #     send_mail_actual_function = self.send_mail_function
        # else:
        # Import a function from its dotted path
        mod, _, function = self.send_mail_function.rpartition('.')

        mod = import_module(mod)

        send_mail_actual_function = getattr(mod, function)

        return send_mail_actual_function(*args, **kwargs)


class SendMailMixin(KeyMixin, SendMailFunctionMixin):
    def test_send_mail_key_validation_fail_raises_exception(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        from secure_mail import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                html_message=mark_safe(msg_html))
        utils.encrypt_kwargs['always_trust'] = previous_value

    def test_send_mail_function_txt_message(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to)

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_txt_message_with_unencrypted_recipients(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com', 'unencrypted@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to)

        # Grab the unencrypted message
        unencrypted_messages = (msg for msg in mail.outbox if to[1] in msg.to)

        message = next(unencrypted_messages, None)

        self.assertEqual(message.subject, msg_subject)
        self.assertEqual(message.body, msg_text)
        self.assertEqual(message.to, [to[1]])
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])

        self.assertIsNone(next(unencrypted_messages, None))

        # Grab the encrypted message
        encrypted_messages = (msg for msg in mail.outbox if to[0] in msg.to)

        message = next(encrypted_messages, None)

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, [to[0]])
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])

        self.assertIsNone(next(encrypted_messages, None))

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_txt_message_with_unencrypted_recipients_with_attachment_from_filename(self):  # noqa: E501
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com', 'unencrypted@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[('file.txt', msg_html, 'text/html')])

        # Grab the unencrypted message
        unencrypted_messages = (msg for msg in mail.outbox if to[1] in msg.to)

        message = next(unencrypted_messages, None)

        self.assertEqual(message.subject, msg_subject)
        self.assertEqual(message.body, msg_text)
        self.assertEqual(message.to, [to[1]])
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.alternatives, [])
        self.assertNotEqual(message.attachments, [])

        self.assertIsNone(next(unencrypted_messages, None))

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(filename, 'file.txt')
        self.assertEqual(mimetype, "text/html")
        self.assertEqual(content, msg_html)

        # Grab the encrypted message
        encrypted_messages = (msg for msg in mail.outbox if to[0] in msg.to)

        message = next(encrypted_messages, None)

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, [to[0]])
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.alternatives, [])
        self.assertNotEqual(message.attachments, [])

        self.assertIsNone(next(encrypted_messages, None))

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test it against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)),
                          msg_text)

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(
            filename, 'file.txt{}'.format('.asc' if self.use_asc else ''))
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_html_message(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            html_message=mark_safe(msg_html))

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertNotEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one alternative - the HTML message
        self.assertEqual(len(message.alternatives), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        alt, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(str(self.gpg.decrypt(alt)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_html_message_attachment(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[(None, msg_html, 'text/html')])

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEqual(message.alternatives, [])
        self.assertNotEqual(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(filename, None)
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_html_message_attachment_from_filename(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[('file.txt', msg_html, 'text/html')])

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEqual(message.alternatives, [])
        self.assertNotEqual(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(
            filename, 'file.txt{}'.format('.asc' if self.use_asc else ''))
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(str(self.gpg.decrypt(content)), msg_html)

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')

    def test_send_mail_function_html_message_encrypted_attachment(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            attachments=[(None, msg_html, 'application/gpg-encrypted')])

        message = mail.outbox[0]

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the content to make sure it wasn't encrypted
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(filename, None)
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(content, msg_html)

    def test_send_mail_function_html_message_attachment_from_mime(self):
        self.maxDiff = 10000
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        attachment_filename = 'tests/templates/secure_mail/dr_suess.html'

        message = MIMEBase('text', 'plain', name=basename(attachment_filename))

        with open(attachment_filename, 'r') as f:
            message.set_payload(f.read())

        self.send_mail(msg_subject, msg_text, from_email, to,
                       attachments=[message])

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext so we fail quickly
        self.assertNotEqual(message.body, "")
        self.assertNotEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.from_email, from_email)
        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertEqual(message.alternatives, [])
        self.assertNotEqual(message.attachments, [])

        # Import the private key so we can decrypt the message body to test it
        import_result = self.gpg.import_keys(TEST_PRIVATE_KEY)

        self.assertTrue(all([result.get('ok', False)
                             for result in import_result.results]))

        keys = self.gpg.list_keys()
        imported_key = keys.key_map[TEST_KEY_FINGERPRINT]
        fp = imported_key['fingerprint']

        self.assertEqual(fp, TEST_KEY_FINGERPRINT)

        # Decrypt and test the message body against the cleartext
        self.assertEqual(str(self.gpg.decrypt(message.body)), msg_text)

        # We should only have one attachment - the HTML message
        self.assertEqual(len(message.attachments), 1)

        # Check the mimetype, then decrypt the contents and compare it to the
        # cleartext
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(
            filename, '{}{}'.format(
                basename(attachment_filename),
                '.asc' if self.use_asc else ''))
        self.assertEqual(mimetype, "application/gpg-encrypted")
        with open(attachment_filename, 'r') as f:
            self.assertEqual(str(self.gpg.decrypt(content)), f.read())

        # Clean up the private key we imported here, leave the public key to be
        # cleaned up by tearDownClass
        delete_result = self.gpg.delete_keys(
            TEST_KEY_FINGERPRINT, secret=True,
            passphrase=SIGNING_KEY_PASSPHRASE)

        self.assertEqual(str(delete_result), 'ok')
