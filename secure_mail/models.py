from django.db import models
from django.utils.translation import gettext_lazy as _

from secure_mail.settings import SIGNING_KEY_PASSPHRASE
from secure_mail.utils import addresses_for_key, get_gpg


class Key(models.Model):
    """
    Accepts a key and imports it via admin's save_model which
    omits saving.
    """

    class Meta:
        verbose_name = _("Key")
        verbose_name_plural = _("Keys")

    key = models.TextField()
    fingerprint = models.CharField(max_length=200, blank=True,
                                   editable=False)
    use_asc = models.BooleanField(default=False, help_text=_(
        "If True, an '.asc' extension will be added to email attachments "
        "sent to the address for this key."))

    def __str__(self):
        return self.fingerprint

    @property
    def email_addresses(self):
        return ",".join(str(address) for address in self.address_set.all())

    def save(self, *args, **kwargs):
        gpg = get_gpg()
        result = gpg.import_keys(self.key)

        addresses = []
        for key in result.results:
            addresses.extend(addresses_for_key(gpg, key))

        self.fingerprint = result.fingerprints[0]

        super(Key, self).save(*args, **kwargs)
        for address in addresses:
            address, _ = Address.objects.get_or_create(
                key=self,
                address=address)
            address.use_asc = self.use_asc
            address.save()


class Address(models.Model):
    """
    Stores the address for a successfully imported key and allows
    deletion.
    """

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    address = models.EmailField(blank=True)
    key = models.ForeignKey('secure_mail.Key', null=True, editable=False,
                            on_delete=models.deletion.CASCADE)
    use_asc = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.address

    def delete(self):
        """
        Remove any keys for this address.
        """
        gpg = get_gpg()
        for key in gpg.list_keys():
            if self.address in addresses_for_key(gpg, key):
                gpg.delete_keys(key["fingerprint"], secret=True,
                                passphrase=SIGNING_KEY_PASSPHRASE)
                gpg.delete_keys(key["fingerprint"])
        super(Address, self).delete()
