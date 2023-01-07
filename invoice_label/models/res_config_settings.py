# Copyright 2017-2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_labels_width = fields.Float(
        related='company_id.invoice_labels_width', required=True,
        readonly=False,
    )
    invoice_labels_height = fields.Float(
        related='company_id.invoice_labels_height', required=True,
        readonly=False,
    )
    invoice_labels_padding = fields.Float(
        related='company_id.invoice_labels_padding', required=True,
        readonly=False,
    )
    invoice_labels_margin_top = fields.Float(
        related='company_id.invoice_labels_margin_top',
        required=True, readonly=False,
    )
    invoice_labels_margin_bottom = fields.Float(
        related='company_id.invoice_labels_margin_bottom',
        required=True, readonly=False,
    )
    invoice_labels_margin_left = fields.Float(
        related='company_id.invoice_labels_margin_left',
        required=True, readonly=False,
    )
    invoice_labels_margin_right = fields.Float(
        related='company_id.invoice_labels_margin_right',
        required=True, readonly=False,
    )
    invoice_labels_paperformat_id = fields.Many2one(
        'report.paperformat', string='Paperformat', required=True,
        default=lambda self: self.env.ref(
            'invoice_label.report_res_invoice_label'
        ).paperformat_id,
        compute='_compute_invoice_labels_paperformat_id',
        inverse='_inverse_invoice_labels_paperformat_id',
    )

    @api.multi
    def _compute_invoice_labels_paperformat_id(self):
        for this in self:
            this.invoice_labels_paperformat_id = self.env.ref(
                'invoice_label.report_res_invoice_label'
            ).paperformat_id

    @api.multi
    def _inverse_invoice_labels_paperformat_id(self):
        for this in self:
            self.env.ref(
                'invoice_label.report_res_invoice_label'
            ).paperformat_id = this.invoice_labels_paperformat_id

    @api.multi
    def action_invoice_labels_preview(self):
        return self.env.ref(
            'invoice_label.report_res_invoice_label'
        ).report_action(
            self.env['account.invoice'].search([], limit=100),
        )
