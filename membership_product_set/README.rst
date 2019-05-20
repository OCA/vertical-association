.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===============================================
Membership Set
===============================================

This module enable the user to define a Set of Memberships and
create the summarized invoice. 


Usage
=====

The module adds a boolean field "Membership set" in model "product.template".
Once it was set, the User can define the membership set by adding the normal
memberships in field "Membership products".

The module extends the wizard "Buy membership" for creating
a summarized invoice, which contains the invoice lines for each
membership in the selected Membership set.

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/vertical-association/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Yu Weng <yweng@elegosoft.com>

Do not contact contributors directly about support or help with technical issues.

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
