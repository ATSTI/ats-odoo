from odoo import _, api, fields, models
from odoo.exceptions import UserError

class DocumentNfe(models.Model):
    _inherit = "l10n_br_fiscal.document"

    # @api.depends("move_ids", "move_ids.financial_move_line_ids")
    # def _compute_nfe40_dup(self):        
    #     for record in self.filtered(lambda x: x._need_compute_nfe40_dup()):
    #         if (record.move_ids.ref and record.move_ids.invoice_origin and 
    #             record.move_ids.ref == "NFe-" + record.move_ids.invoice_origin):
    #             dups_vals = []
    #             #            "nfe40_vDup": mov.debit,
    #             for count, mov in enumerate(record.move_ids.financial_move_line_ids, 1):
    #                 dups_vals.append(
    #                     {
    #                         "nfe40_nDup": str(count).zfill(3),
    #                         "nfe40_dVenc": mov.date_maturity,
    #                         "nfe40_vDup": record.amount_total,
    #                     }
    #                 )
    #             record.nfe40_dup = [(2, dup, 0) for dup in record.nfe40_dup.ids]
    #             record.nfe40_dup = [(0, 0, dup) for dup in dups_vals]
    #         else:
    #             super()._compute_nfe40_dup()

    def action_view_invoice(self):
        self.ensure_one()
        form_view_name = "account.view_move_form"

        if not self.move_ids or not self.move_ids[0].move_type:
            return
        move_type = self.move_ids[0].move_type
        xmlid = f"account.action_move_{move_type}_type"
        if move_type == 'entry':
            xmlid = f"account.action_move_out_invoice_type"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)

        if len(self.move_ids) > 1:
            action["domain"] = "[('id', 'in', %s)]" % self.move_ids.ids
        else:
            form_view = self.env.ref(form_view_name)
            action['views'] = [(form_view.id, "form")]
            res_id = self.move_ids.id
            if move_type == 'entry':
                res_id_move = self.env['account.move'].search([('name', '=', self.move_ids[0].invoice_origin)], limit=1)
                if res_id_move and res_id != res_id_move.id:
                    res_id = res_id_move.id
            action["res_id"] = res_id

        return action
