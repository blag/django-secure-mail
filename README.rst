.. image:: https://travis-ci.org/blag/django-secure-mail.svg?branch=master
    :target: https://travis-ci.org/blag/django-secure-mail

.. image:: https://coveralls.io/repos/github/blag/django-secure-mail/badge.svg
    :target: https://coveralls.io/github/blag/django-secure-mail


Created by `blag <http://github.com/blag>`_. Forked from PR
`#39 <https://github.com/stephenmcd/django-email-extras/pull/39>`_ and
`#40 <https://github.com/stephenmcd/django-email-extras/pull/40>`_ of
`django-email-extras <https://github.com/stephenmcd/django-email-extras>`_ by
`Stephen McDonald <http://twitter.com/stephen_mcd>`_.

Introduction
============

django-secure-mail is a Django reusable app providing a mail backend to send
opportunistically signed and encrypted emails using PGP. Also provided are
models and an admin page to manage uploaded PGP keys.

Note that the provided backend only signs outgoing mail if the recipient has
uploaded a valid public key. Users without valid public keys will *not* have
their outgoing mail signed or encrypted.


Dependencies
============

* `python-gnupg <https://bitbucket.org/vinay.sajip/python-gnupg>`_ is
  required for sending PGP encrypted email.


Installation
============

The easiest way to install django-secure-mail is directly from PyPi
using `pip <https://pip.pypa.io/en/stable/>`_ by running the command
below:

.. code-block:: bash

    $ pip install django-secure-mail

Otherwise you can download django-secure-mail and install it directly
from source:

.. code-block:: bash

    $ python setup.py install


Configuration
=============

1. Add ``secure_mail`` to your ``INSTALLED_APPS`` setting and run database
   migrations:

    .. code-block:: bash

        $ python manage.py migrate secure_mail

2. Set ``EMAIL_BACKEND`` in your settings module to
   ``secure_mail.backends.EncryptingSmtpEmailBackend`` or one of the
   development/testing backends listed in `Development and Testing`_.

3. Set the ``SECURE_MAIL_GNUPG_HOME`` setting to a directory that contains the
   GPG keyring. If you are running multiple Django nodes, each node will need
   read *and write* access to this directory.

4. Set the ``SECURE_MAIL_GNUPG_ENCODING`` variable to the encoding your GPG
   executable requires. This is generally ``latin-1`` for GPG 1.x and ``utf-8``
   for GPG 2.x.

5. Whle it is not required to send encrypted email, it is *highly recommended*
   that you generate a signing key for outgoing mail. Please follow the
   instructions in the `Generate Signing Key`_ section. All nodes that will
   be sending outgoing mail will need to have read access to the directory
   specified by ``SECURE_MAIL_GNUPG_HOME``.

There are additional configuration options available. Please see the `Options`_
section for a complete list.


Generate Signing Key
--------------------

Adding a private/public signing keypair is different than importing a
public encryption key, since the private key will be stored on the
server.

This project ships with a Django management command to generate and
export signing keys: ``email_signing_key``.

You first need to set the ``SECURE_MAIL_SIGNING_KEY_DATA`` option in your
project's ``settings.py``. This is a dictionary that is passed as keyword arguments directly to ``GPG.gen_key()``, so please read and understand all of
the available `options in their documentation <https://pythonhosted.org/python-gnupg/#generating-keys>`_. The default settings are:

.. code-block:: python

    SECURE_MAIL_SIGNING_KEY_DATA = {
        'key_type': "RSA",
        'key_length': 4096,
        'name_real': settings.SITE_NAME,
        'name_comment': "Outgoing email server",
        'name_email': settings.DEFAULT_FROM_EMAIL,
        'expire_date': '2y',
    }

You may wish to change the ``key_type`` to a signing-only type of key,
such as DSA, or the expire date.

Once you are content with the signing key settings, generate a new
signing key with the ``--generate`` option:

.. code-block:: bash

    $ python manage.py email_signing_key --generate

To work with specific keys, identify them by their fingerprint

.. code-block:: bash

    $ python manage.py email_signing_key 7AB59FE794A7AC12EBA87507EF33F601153CFE28

You can print the private key to your terminal/console with:

.. code-block:: bash

    $ python manage.py email_signing_key 7AB59FE794A7AC12EBA87507EF33F601153CFE28 --print-private-key

And you can upload the public signing key to one or more specified
keyservers by passing the key server hostnames with the ``-k`` or
``--keyserver`` options:

.. code-block:: bash

    $ python manage.py email_signing_key 7AB59FE794A7AC12EBA87507EF33F601153CFE28 -k keys.ubuntu.com keys.redhat.com -k pgp.mit.edu

You can also perform all tasks with one command:

.. code-block:: bash

    $ python manage.py email_signing_key --generate --keyserver pgp.mit.edu --print-private-key

Use the ``--help`` option to see the complete help text for the command.

Once you have generated the signing key, you will need to configure
``secure_mail`` to use it. Set the ``SECURE_MAIL_KEY_FINGERPRINT`` setting to
the fingerprint of the outgoing signing key you wish to use. 


Options
-------

There are a few settings you can configure in your project's
``settings.py`` module:

* ``SECURE_MAIL_GNUPG_HOME`` - String representing a custom location
  for the GNUPG keyring. If you are running multiple Django nodes, this should
  be set to a directory shared by all nodes, and the ``gpg`` executable on all
  nodes will need read and write access to it.
* ``SECURE_MAIL_USE_GNUPG`` - Boolean that controls whether the PGP
  encryption features are used. Defaults to ``True`` if
  ``SECURE_MAIL_GNUPG_HOME`` is specified, otherwise ``False``.
* ``SECURE_MAIL_GNUPG_ENCODING`` - The encoding the local ``gpg`` executable
  expects. This option is passed through to the ``str.encode`` function. In
  general, it should be set to ``latin-1`` for GPG 1.x and ``utf-8`` for GPG
  2.x. Check out
  `python-gnupg documentation <https://pythonhosted.org/python-gnupg/#getting-started>`_
  for more info.
* ``SECURE_MAIL_FAILURE_HANDLERS`` - A dictionary that maps failed types to the
  dotted-path notation of error handlers. See the `Error Handling`_ section for
  details and an example.
* ``SECURE_MAIL_ALWAYS_TRUST_KEYS`` - Skip key validation and assume that used
  keys are always fully trusted. This simply sets ``--always-trust`` (or
  ``--trust-model`` for more modern versions of GPG). See the GPG documentation
  on the ``--trust-model`` option for more detail about this setting.
* ``SECURE_MAIL_SIGNING_KEY_DATA`` - A dictionary of key options for generating
  new signing keys. See the
  `python-gnupg documentation https://pythonhosted.org/python-gnupg`_ for more
  details.

  Default:

    .. code-block:: python

        {
            'key_type': "RSA",
            'key_length': 4096,
            'name_real': settings.SITE_NAME,
            'name_comment': "Outgoing email server",
            'name_email': settings.DEFAULT_FROM_EMAIL,
            'expire_date': '2y',
        }

* ``SECURE_MAIL_KEY_FINGERPRINT`` - The fingerprint of the key to use when
  signing outgoing mail, must exist in the configured keyring.


Sending PGP Encrypted Email
===========================

Once the backend is configured and specified by the ``EMAIL_BACKEND`` setting,
all outgoing mail will be opportunistically signed and encrypted. This means
that if a message is being sent to a recipient who has a valid public key in
the database and the GPG/PGP keyring, the backend will attempt to sign and
encrypt outgoing mail to them.


Error Handling
==============

This backend allows users to specify custom error handlers when encryption
fails for the following objects:

* The plain text message itself
* Any message attachments
* Any message alternatives (for instance: HTML mail delivered with a plain text
  fallback)

Error handlers are called when an exception is raised and are passed the raised
exception.

.. code-block:: python

    def handle_failed_encryption(exception):
        # Handle errors

    def handle_failed_alternative_encryption(exception):
        # Handle errors

    def handle_failed_attachment_encryption(exception):
        # Handle errors

The default error handlers simply re-raise the exception, but this may be
undesirable for all cases.

To assist with handling errors, the package provides a few helper functions
that can be used in custom error handlers:

* ``force_send_message`` - Accepts the unencrypted message as an argument,
  and sends the message without attempting to encrypt or sign it.
* ``force_delete_key`` - Accepts the recipient's address as an argument and
  forcibly removes all keys from the database and the GPG/PGP keyring.
* ``force_mail_admins`` - Accepts the unencrypted message and the failing
  address as arguments. If the address is in the ``ADMINS`` setting, it sends
  the message unencrypted, otherwise, it mails the admins a message containing
  the subject of the original message and the original intended recipient.
* ``get_variable_from_exception`` - Accepts the exception and a variable name
  as arguments, then digs back through the stacktrace to find the first
  variable with the specified name.

To specify a custom error handlers, set keys in the
``SECURE_MAIL_FAILURE_HANDLERS`` setting dictionary in your project's
``settings.py`` to the dotted-path of your error handler/s:

.. code-block:: python

    SECURE_MAIL_FAILURE_HANDLERS = {
        'message': 'myapp.handlers.handle_failed_encryption',
        'alternative': 'myapp.handlers.handle_failed_alternative_encryption',
        'attachment': 'myapp.handlers.handle_failed_attachment_encryption',
    }

You do not have to override all of the handlers, you can override as many or as
few as you wish.


Development and Testing
=======================

This package provides a backend mixin (``EncryptingEmailBackendMixin``) if you
wish to extend the backend or create a custom backend of your own:

.. code-block:: python

    class EncryptingLocmemEmailBackend(EncryptingEmailBackend, LocmemBackend):
        pass

For a working, real-world example of using the ``EncryptingEmailBackendMixin``
in another Django app, check out the
``emailhub.backends.secure_mail.EncryptingEmailBackendMixin`` from the
`django-emailhub <https://github.com/FIXME/django-emailhub>`_ project:

In addition to the provided ``EncryptingSmtpEmailBackend``, this package ships
with a few more backends that mirror the built-in Django backends:

* ``EncryptingConsoleEmailBackend``
* ``EncryptingLocmemEmailBackend``
* ``EncryptingFilebasedEmailBackend``


Database Models
---------------

`PGP explanation <https://en.wikipedia.org/wiki/Pretty_Good_Privacy>`_

Using `python-gnupg`_, two models are defined in ``secure_mail.models`` -
``Key`` and ``Address`` which represent a PGP key and an email address for a
successfully imported key. These models exist purely for the sake of importing
keys and removing keys for a particular address via the Django
Admin.

When adding a key, the key is imported into the key ring on
the server and the instance of the ``Key`` model is not saved. The
email address for the key is also extracted and saved as an
``Address`` instance.

The ``Address`` model is then used when sending email to check for
an existing key to determine whether an email should be encrypted.
When an ``Address`` is deleted via the Django Admin, the key is
removed from the key ring on the server.


Alternative Django Apps
=======================

Other Django apps with similar functionality are:

* `django-email-extras <https://github.com/stephenmcd/django-email-extras>`_ -
  Provides two functions for sending PGP encrypted, multipart emails using
  Django's template system. Also provides a mail backend that displays HTML
  mail in the browser during development.
* `django-gnupg-mails <https://github.com/jandd/django-gnupg-mails>`_ -
  Provides a ``GnuPGMessage`` (subclass of Django's ``EmailMessage``) to send
  PGP/MIME signed email.

Both of those apps require third party app developers to "opt-in" to sending
encrypted mail. This project automatically encrypts and signs all outgoing mail
for all apps.
