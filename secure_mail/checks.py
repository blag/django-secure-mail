from django.core.checks import Tags, Error

from secure_mail.settings import (
    GNUPG_HOME, SIGNING_KEY_FINGERPRINT, USE_GNUPG
)
from secure_mail.utils import get_gpg


class SecureMailTags(Tags):
    mail = 'mail'


def check_signing_key(app_configs, **kwargs):
    errors = []
    if USE_GNUPG and SIGNING_KEY_FINGERPRINT is not None:
        gpg = get_gpg()
        try:
            gpg.list_keys(True).key_map[SIGNING_KEY_FINGERPRINT]
        except (AttributeError, KeyError):
            errors = [
                Error("The key specified by the "
                      "SECURE_MAIL_SIGNING_KEY_FINGERPRINT setting ({fp}) "
                      "does not exist in the GPG keyring.".format(
                          fp=SIGNING_KEY_FINGERPRINT),
                      hint="Adjust the SECURE_MAIL_GNUPG_HOME setting "
                           "(currently set to {gnupg_home}, correct the key "
                           "fingerprint, or generate a new key by running "
                           "python manage.py email_signing_key --generate "
                           "to fix.".format(gnupg_home=GNUPG_HOME),
                      id='secure_mail.E0001')
            ]
    return errors
