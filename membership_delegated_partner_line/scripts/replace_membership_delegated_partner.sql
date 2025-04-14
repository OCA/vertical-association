-- This module is incompatible with `membership_delegated_partner` and any module that depends
-- on it. Prior to installing this module, if you use membership_delegated_partner:
--
-- 1.  Prior to uninstalling `membership_delegated_partner` and installing this one,
--     run this following SQL instructions `replace_membership_delegated_partner.sql`.
-- 2.  Uninstall `membership_delegated_partner`.
-- 3.  Install this module.

-- This request add and set delegated member on account.move.lines from account.move.

ALTER TABLE account_move_line ADD COLUMN IF NOT EXISTS delegated_member_id int4;
UPDATE account_move_line SET delegated_member_id = am.delegated_member_id
    FROM account_move am, product_product p, product_template pt
    WHERE am.id = account_move_line.move_id
      AND am.delegated_member_id IS NOT NULL
      AND account_move_line.delegated_member_id IS NULL
      AND p.id=account_move_line.product_id
      AND p.product_tmpl_id = pt.id
      AND pt.membership = TRUE
      AND account_move_line.exclude_from_invoice_tab = FALSE;
