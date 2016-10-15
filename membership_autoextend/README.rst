.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=====================
Autoextend membership
=====================

This module was written to define membership products as being autoextended.

Members with a membership of this type will be informed before an extension takes place in order to give them the chance to cancel their membership.

Configuration
=============

To configure this module, you need to:

* go to a membership product
* check box ``Autoextend membership``
* optionally set email templates to inform a member about an upcoming extension and after it's done
* optionally set an amount of days before the extension the warning mail should be sent
* if you select an extension membership, this product will be used to extend the membership. Otherwise, the current membership product will be used

Note that this module is not strictly necessary for automatic extensions, you can have the same effect with the modules ``subscription`` and ``membership_variable_period``.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/208/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/vertical-association/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/vertical-association/issues/new?body=module:%20membership_autoextend%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
