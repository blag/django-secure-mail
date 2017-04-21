from django.contrib import admin

from secure_mail.forms import KeyForm
from secure_mail.models import Key, Address


class KeyAdmin(admin.ModelAdmin):
    form = KeyForm
    list_display = ('__str__', 'email_addresses')
    readonly_fields = ('fingerprint',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'key')
    readonly_fields = ('key',)

    def has_add_permission(self, request):
        return False


admin.site.register(Key, KeyAdmin)
admin.site.register(Address, AddressAdmin)
