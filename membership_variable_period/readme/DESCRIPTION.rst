Current membership module allows to set products that define a fixed period
for a membership. This is good when the quotas are defined periodically, and
when you become a member, you are until the end of that quota cycle.

But a lot of times, membership quotas express an amount of time that you
gain the membership. For example, one year since the subscription.

This module allows to make it in Odoo, using current membership features,
and adapting them for this purpose. As now the quota is not attached to a fixed
period, you can also invoice more than one quantity for being a member for
the corresponding number of periods.

Finally, a cron has been included that triggers the recalculation of the
membership state, allowing to have "old members", which doesn't work well
on standard.
