from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardValidarConferencia(models.TransientModel):
    _name = 'wizard.validar.conferencia'
    _description = 'Validar Conferência'

    picking_id = fields.Many2one('stock.picking', readonly=True)
    tem_divergencia = fields.Boolean(readonly=True)
    line_ids = fields.One2many(
        'wizard.validar.conferencia.line',
        'wizard_id',
        string='Divergências',
        readonly=True,
    )

    def action_confirmar(self):
        self.ensure_one()
        self.picking_id.write({
        'conferencia_validada': True,
        'state': 'done',
        })
        return {'type': 'ir.actions.act_window_close'}

    def action_imprimir_divergentes(self):
        self.ensure_one()

        if self.tem_divergencia:
            return self.env.ref(
                'report_soloz.report_stockpicking_orcamento'
            ).report_action(self.picking_id)

        self.picking_id.write({
            'conferencia_validada': True,
            'state': 'done',
        })

        return {'type': 'ir.actions.act_window_close'}

class WizardValidarConferenciaLine(models.TransientModel):
    _name = 'wizard.validar.conferencia.line'
    _description = 'Linha de Divergência'

    wizard_id = fields.Many2one('wizard.validar.conferencia')
    product_id = fields.Many2one('product.product', string='Produto', readonly=True)
    qty_conferida = fields.Float(string='Qtd Conferida', readonly=True)