from secure_mail.settings import (ALWAYS_TRUST, GNUPG_ENCODING, GNUPG_HOME,
                                  USE_GNUPG, SIGNING_KEY_FINGERPRINT)

if USE_GNUPG:
    from gnupg import GPG

    def get_gpg():
        gpg = GPG(gnupghome=GNUPG_HOME)
        if GNUPG_ENCODING is not None:
            gpg.encoding = GNUPG_ENCODING
        return gpg

# Used internally
encrypt_kwargs = {
    'always_trust': ALWAYS_TRUST,
    'sign': SIGNING_KEY_FINGERPRINT,
}


class EncryptionFailedError(Exception):
    pass


class BadSigningKeyError(KeyError):
    pass


def check_signing_key():
    if USE_GNUPG and SIGNING_KEY_FINGERPRINT is not None:
        gpg = get_gpg()
        try:
            gpg.list_keys(True).key_map[SIGNING_KEY_FINGERPRINT]
        except KeyError:
            raise BadSigningKeyError(
                "The key specified by the "
                "SECURE_MAIL_SIGNING_KEY_FINGERPRINT setting "
                "({fp}) does not exist in the GPG keyring. Adjust the "
                "SECURE_MAIL_GNUPG_HOME setting (currently set to "
                "{gnupg_home}, correct the key fingerprint, or generate a new "
                "key by running python manage.py email_signing_key --generate "
                "to fix.".format(
                    fp=SIGNING_KEY_FINGERPRINT,
                    gnupg_home=GNUPG_HOME))


def addresses_for_key(gpg, key):
    """
    Takes a key and extracts the email addresses for it.
    """
    return [address.split("<")[-1].strip(">")
            for address in gpg.list_keys().key_map[key['fingerprint']]["uids"]
            if address]
