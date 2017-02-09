.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Membership extension
====================

This module extends Odoo's membership management with the following features:

* Membership category
* Membership lines editable
* Do not calculate membership state from invoice status
* Start date of last membership period

Configuration
=============

Users can define membership categories in Association > Configuration > Membership Categories
Then go to membership products and set a category to each one

Usage
=====

Membership categories allow to classify memberships by types, allowing a
partner to be member or not of the different categories. For example, if you
have several levels of partnership (Starter, Silver, Gold) and one product
for each one, then partners who buy Silver product will have Silver membership
category. Afterwords, you can filter Silver members.

Membership lines are created when a membership product is invoiced, like in
Odoo standard version. But now users can create a new membership line without
creating an invoice.

Also, users can edit membership line dates and state even if an invoice is
not related with it.

You will see a general membership status at partner level that specifies if
it's a member of any category or not, and also a detail status per
membership category.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/208/8.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/vertical-association/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Antonio Espinosa <antonio.espinosa@tecnativa.com>
* Pedro M. Baeza <pedro.baeza@tecnativa.com>

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
