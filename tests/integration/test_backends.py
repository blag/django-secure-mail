from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils.safestring import mark_safe

from secure_mail.utils import EncryptionFailedError

from tests.utils import (
    DeleteAllKeysMixin, KeyMixin, SendMailFunctionMixin, SendMailMixin
)


@override_settings(
    EMAIL_BACKEND='secure_mail.backends.EncryptingLocmemEmailBackend')
class SendEncryptedMailBackendWithUseGnuPGFalseTestCase(
        KeyMixin, SendMailFunctionMixin, DeleteAllKeysMixin, TestCase):
    use_asc = True
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def test_send_mail_function_html_message(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        from secure_mail import backends
        previous_value = backends.USE_GNUPG
        backends.USE_GNUPG = False

        self.send_mail(msg_subject, msg_text, from_email, to)

        backends.USE_GNUPG = previous_value

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]

        self.assertEqual(message.body, msg_text)


@override_settings(
    EMAIL_BACKEND='secure_mail.backends.EncryptingLocmemEmailBackend')
class SendEncryptedMailBackendNoASCTestCase(SendMailMixin, TestCase):
    use_asc = False
    maxDiff = 10000
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def test_send_mail_function_html_message_encrypted_alternative(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        with open('tests/templates/secure_mail/dr_suess.txt', 'r') as f:
            alt = f.read()

        self.send_mail(
            msg_subject, msg_text, from_email, to,
            alternatives=[(alt, 'application/gpg-encrypted')])

        message = mail.outbox[0]

        # Decrypt and test the alternatives later, just ensure we have
        # any alternatives at all so we fail quickly
        self.assertNotEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])

        # We should only have one alternative - the txt message
        self.assertEqual(len(message.alternatives), 1)

        # Check the alternative to make sure it wasn't encrypted
        content, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "application/gpg-encrypted")
        self.assertEqual(content, alt)

    def test_handle_failed_alternative_encryption(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sending the mail fail
        from secure_mail import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        # Tweak the failed content handler to simply pass
        from secure_mail import backends
        previous_content_handler = backends.handle_failed_message_encryption
        backends.handle_failed_message_encryption = lambda e: None
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                html_message=mark_safe(msg_html))
        backends.handle_failed_message_encryption = previous_content_handler
        utils.encrypt_kwargs['always_trust'] = previous_value

    def test_handle_failed_attachment_encryption(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"
        msg_html = "<html><body><b>Hello</b> World <i>Text</i>"

        # Make sending the mail fail
        from secure_mail import utils
        previous_value = utils.encrypt_kwargs['always_trust']
        utils.encrypt_kwargs['always_trust'] = False
        # Tweak the failed content handler to simply pass
        from secure_mail import backends
        previous_content_handler = backends.handle_failed_message_encryption
        backends.handle_failed_message_encryption = lambda e: None
        with self.assertRaises(EncryptionFailedError):
            self.send_mail(
                msg_subject, msg_text, from_email, to,
                attachments=[('file.txt', msg_html, 'text/html')])
        backends.handle_failed_message_encryption = previous_content_handler
        utils.encrypt_kwargs['always_trust'] = previous_value


@override_settings(
    EMAIL_BACKEND='secure_mail.backends.EncryptingLocmemEmailBackend')
class SendEncryptedMailBackendWithASCTestCase(SendMailMixin, TestCase):
    use_asc = True
    send_mail_function = 'tests.utils.send_mail_with_backend'


@override_settings(
    EMAIL_BACKEND='secure_mail.backends.EncryptingLocmemEmailBackend')
class SendDoNotEncryptMailBackendTestCase(SendMailMixin, TestCase):
    use_asc = True
    send_mail_function = 'tests.utils.send_mail_with_backend'

    def test_send_mail_function_txt_message(self):
        msg_subject = "Test Subject"
        to = ['django-secure-mail@example.com']
        from_email = settings.DEFAULT_FROM_EMAIL
        msg_text = "Test Body Text"

        self.send_mail(msg_subject, msg_text, from_email, to,
                       do_not_encrypt_this_message=True)

        message = mail.outbox[0]

        self.assertEqual(message.subject, msg_subject)
        # We decrypt and test the message body below, these just ensure the
        # message body is not cleartext
        self.assertEqual(message.body, msg_text)
        self.assertEqual(message.to, to)
        self.assertEqual(message.cc, [])
        self.assertEqual(message.bcc, [])
        self.assertEqual(message.reply_to, [])
        self.assertEqual(message.from_email, from_email)
        self.assertEqual(message.extra_headers, {})
        self.assertEqual(message.alternatives, [])
        self.assertEqual(message.attachments, [])
