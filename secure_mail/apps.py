from django.apps import AppConfig
from django.core.checks import register, Tags

from .checks import (check_signing_key, check_can_import_gpg, SecureMailTags)


class SecureMailConfig(AppConfig):
    name = 'secure_mail'
    verbose_name = 'Secure Mail'

    def ready(self):  # pragma: noqa
        # Fail early and loudly if the signing key fingerprint is misconfigured
        register(SecureMailTags.config)(check_can_import_gpg)
        register(SecureMailTags.mail, Tags.security)(check_signing_key)
