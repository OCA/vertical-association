.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=====================
Membership extra info
=====================

This module extends the functionality of membership to add extra useful
membership information

A partner could be member in one period (from Jan 2001 to Oct 2003) and then
signup again two years later (from Feb 2005). Standard Odoo membership addon
considers membership start date as Jan 2001, instead of Feb 2005.

Also a partner could request us for decline his membership (Ago 2006) but
desire to end his membership later (Sep 2006) and we can classify decline
reasons for later analysis

An finally we can define different membership categories, for instance,
Bronce, Silver and Gold. Membership product could be related with a membership
category, so partner membership category is the last membership line product category

* Membership last start date: Start date of last membership period, Feb 2005 in our example
* Membership decline date: Decline date of current membership period, Ago 2006 in our example
* Membership decline reason: Decline reason of current membership period, from an admin defined list of reasons
* Membership category: Membership category of current membership period, from an admin defined list of categories


Configuration
=============

You can define decline reasons at Association > Configuration > Membership decline reasons,
to be selected when a partner requests us to decline his membership

You can define membership categories at Association > Configuration > Membership categories,
to be selected in membership product form


Usage
=====

When a partner has a valid (paid) membership line a new button (X) appears. Click
on it when partner request us to decline his membership. Then a pop-up appears to
define:

* Decline date: Request date, normally today
* New finish date: Finish date of current membership period requested by partner
* Decline reason

After that you can create a refund if necessary, clicking at membership line
invoice and clicking at 'Ask Refund' button.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/208/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/vertical_association/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/vertical_association/issues/new?body=module:%20membership_extra_info%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Antonio Espinosa <antonioea@antiun.com>

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
