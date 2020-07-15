from gnupg import GPG

from secure_mail.settings import (ALWAYS_TRUST,
                                  GNUPG_BINARY, GNUPG_ENCODING, GNUPG_HOME,
                                  SIGNING_KEY_FINGERPRINT,
                                  SIGNING_KEY_PASSPHRASE)


# Used internally
encrypt_kwargs = {
    'always_trust': ALWAYS_TRUST,
    'sign': SIGNING_KEY_FINGERPRINT,
}

delete_kwargs = {'passphrase': SIGNING_KEY_PASSPHRASE}


def get_gpg():
    gpg_kwargs = {
        'gnupghome': GNUPG_HOME,
    }
    if GNUPG_BINARY:
        gpg_kwargs['gpgbinary'] = GNUPG_BINARY
    gpg = GPG(**gpg_kwargs)
    if GNUPG_ENCODING is not None:
        gpg.encoding = GNUPG_ENCODING
    return gpg


class EncryptionFailedError(Exception):
    pass


def addresses_for_key(gpg, key):
    """
    Takes a key and extracts the email addresses for it.
    """
    return [address.split("<")[-1].strip(">")
            for address in gpg.list_keys().key_map[key['fingerprint']]["uids"]
            if address]
