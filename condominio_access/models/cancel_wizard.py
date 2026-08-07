from odoo import fields, models, _

class VisitorCancelWizard(models.TransientModel):
    _name = "condo.visitor.cancel.wizard"
    _description = "Justificativa de Cancelamento"

    visitor_id = fields.Many2one("condo.visitor", required=True)
    motivo = fields.Text(string="Justificativa", required=True)

    def action_confirm(self):
        self.ensure_one()

        self.visitor_id.status = "cancelado"
        self.visitor_id.data_saida = fields.Datetime.now()

        self.visitor_id.message_post(
            body=_(
                "<b>Visita cancelada</b><br/>"
                "<b>Justificativa:</b><br/>%s"
            ) % self.motivo,
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        self.visitor_id.cancel_reason = self.motivo

        return {"type": "ir.actions.act_window_close"}