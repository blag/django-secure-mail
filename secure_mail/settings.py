from django.conf import settings


# DEFAULT_FAILURE_HANDLERS = {
#     'message': 'secure_mail.handlers.default_handle_failed_encryption',
#     'alternative': 'secure_mail.handlers.default_handle_failed_alternative_encryption',  # noqa: E501
#     'attachment': 'secure_mail.handlers.default_handle_failed_attachment_encryption',  # noqa: E501
# }
# DEFAULT_SIGNING_KEY_DATA = {
#     'key_type': "RSA",
#     'key_length': 4096,
#     'name_real': getattr(settings, 'SITE_NAME', ''),
#     'name_comment': "Outgoing email server",
#     'name_email': settings.DEFAULT_FROM_EMAIL,
#     'expire_date': '2y',
# }
# DEFAULT_SETTINGS = {
#     'GNUPG_HOME': None,
#     'ALWAYS_TRUST': False,
#     'GNUPG_ENCODING': None,
#     'SIGNING_KEY_FINGERPRINT': None,
# }

# DEFAULT_SETTINGS['USE_GNUPG'] = DEFAULT_SETTINGS['GNUPG_HOME'] is not None


GNUPG_BINARY = getattr(settings, "SECURE_MAIL_GNUPG_BINARY", None)
GNUPG_HOME = getattr(settings, "SECURE_MAIL_GNUPG_HOME", None)
USE_GNUPG = getattr(settings, "SECURE_MAIL_USE_GNUPG", GNUPG_HOME is not None)

ALWAYS_TRUST = getattr(settings, "SECURE_MAIL_ALWAYS_TRUST_KEYS", False)
FAILURE_HANDLERS = {
    'message': 'secure_mail.handlers.default_handle_failed_encryption',
    'alternative': 'secure_mail.handlers.default_handle_failed_alternative_encryption',  # noqa: E501
    'attachment': 'secure_mail.handlers.default_handle_failed_attachment_encryption',  # noqa: E501
}
FAILURE_HANDLERS.update(getattr(settings, "SECURE_MAIL_FAILURE_HANDLERS", {}))
GNUPG_ENCODING = getattr(settings, "SECURE_MAIL_GNUPG_ENCODING", None)
SIGNING_KEY_PASSPHRASE = getattr(settings, "SECURE_MAIL_SIGNING_KEY_PASSPHRASE", '')
SIGNING_KEY_DATA = {
    'key_type': "RSA",
    'key_length': 4096,
    'name_real': getattr(settings, 'SITE_NAME', ''),
    'name_comment': "Outgoing email server",
    'name_email': settings.DEFAULT_FROM_EMAIL,
    'expire_date': '2y',
    'passphrase': SIGNING_KEY_PASSPHRASE,
}
SIGNING_KEY_DATA.update(getattr(settings, "SECURE_MAIL_SIGNING_KEY_DATA", {}))
SIGNING_KEY_FINGERPRINT = getattr(
    settings, "SECURE_MAIL_SIGNING_KEY_FINGERPRINT", None)
