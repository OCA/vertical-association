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
