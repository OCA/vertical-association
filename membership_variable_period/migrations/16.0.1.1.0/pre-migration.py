# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


def migrate(cr, version):
    cr.execute(
        """
        UPDATE product_template
        SET membership_interval_qty = 1
        WHERE membership_interval_qty IS null;
        """
    )
    cr.execute(
        """
        UPDATE product_template
        SET membership_interval_unit = 'years'
        WHERE membership_interval_unit IS null;
        """
    )
