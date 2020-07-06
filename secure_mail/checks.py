from django.core.checks import Tags, Error

from secure_mail.settings import (
    GNUPG_HOME, SIGNING_KEY_FINGERPRINT,
)
from secure_mail.utils import get_gpg


class SecureMailTags(Tags):
    mail = 'mail'
    config = 'config'


def check_signing_key(app_configs, **kwargs):
    errors = []
    if SIGNING_KEY_FINGERPRINT is not None:
        gpg = get_gpg()
        try:
            gpg.list_keys(True).key_map[SIGNING_KEY_FINGERPRINT]
        except (AttributeError, KeyError):
            errors = [
                Error("The key specified by the "
                      "SECURE_MAIL_SIGNING_KEY_FINGERPRINT setting "
                      f"({SIGNING_KEY_FINGERPRINT}) "
                      "does not exist in the GPG keyring.",
                      hint="Adjust the SECURE_MAIL_GNUPG_HOME setting "
                           f"(currently set to {GNUPG_HOME}, correct the key "
                           "fingerprint, or generate a new key by running "
                           "python manage.py email_signing_key --generate "
                           "to fix.",
                      id='secure_mail.E0001')
            ]
    return errors


def check_can_import_gpg(app_configs, **kwargs):
    try:
        import gnupg  # noqa: F401
    except ImportError:  # pragma: no cover
        errors = [Error("Could not import gnupg",
                        hint="Install python-gnupg and ensure gnupg.py is in"
                             "PYTHONPATH",
                        id='secure_mail.E0002')]
    else:
        errors = []
    finally:
        return errors
