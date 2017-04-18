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
PGP signed and encrypted emails. When configured to send PGP encrypted email,
the ability for admin users to manage PGP keys is also provided.


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

    $ pip install -U django-secure-mail

Otherwise you can download django-secure-mail and install it directly
from source:

.. code-block:: bash

    $ python setup.py install


Configuration
=============

Once installed, first add ``secure_mail`` to your ``INSTALLED_APPS``
setting and run the migrations.

Then set ``EMAIL_BACKEND`` in your settings module to
``'secure_mail.backends.EncryptingSmtpEmailBackend'`` or one of the development
and testing backends listed in `Development and Testing`_.

And finally, you can optionally configure `Sending PGP Signed Email`_.


Sending PGP Encrypted Email
===========================

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


Sending PGP Signed Email
========================

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


Options
=======

There are a few settings you can configure in your project's
``settings.py`` module:

* ``SECURE_MAIL_USE_GNUPG`` - Boolean that controls whether the PGP
  encryption features are used. Defaults to ``True`` if
  ``SECURE_MAIL_GNUPG_HOME`` is specified, otherwise ``False``.
* ``SECURE_MAIL_GNUPG_HOME`` - String representing a custom location
  for the GNUPG keyring.
* ``SECURE_MAIL_GNUPG_ENCODING`` - String representing a gnupg encoding.
  Defaults to GNUPG ``latin-1`` and could be changed to e.g. ``utf-8``
  if needed.  Check out
  `python-gnupg docs <https://pythonhosted.org/python-gnupg/#getting-started>`_
  for more info.
* ``SECURE_MAIL_ALWAYS_TRUST_KEYS`` - Skip key validation and assume
  that used keys are always fully trusted.
* ``SECURE_MAIL_SIGNING_KEY_DATA`` - A dictionary of key options for generating
  new signing keys.
* ``SECURE_MAIL_KEY_FINGERPRINT`` - The fingerprint of the key to use when
  signing outgoing mail, must exist in the configured keyring.


Development and Testing
=======================

This package provides a backend mixin if you wish to extend the backend or create a custom backend of your own.

Example:

.. code-block:: python

    class EncryptingLocmemEmailBackend(EncryptingEmailBackend, LocmemBackend):
        pass

In addition to the ``EncryptingSmtpEmailBackend``, backends that mixin every
other built-in Django backend are provided. These are:

* ``EncryptingConsoleEmailBackend``
* ``EncryptingLocmemEmailBackend``
* ``EncryptingFilebasedEmailBackend``


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
