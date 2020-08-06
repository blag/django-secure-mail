
from django import forms
from django.utils.translation import gettext_lazy as _

from secure_mail.models import Key
from secure_mail.utils import get_gpg


class KeyForm(forms.ModelForm):
    class Meta:
        model = Key
        fields = ('key', 'use_asc')

    def clean_key(self):
        """
        Validate the key contains an email address.
        """
        key = self.cleaned_data["key"]
        gpg = get_gpg()
        result = gpg.import_keys(key)
        if result.count == 0:
            raise forms.ValidationError(_("Invalid Key"))
        return key
