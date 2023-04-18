# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "contract.contract"

    def _default_stage_id(self):
        stage_ids = self.env['contract.stage'].\
            search([('is_default', '=', True),
                    ('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if stage_ids:
            return stage_ids[0]
        else:
            raise ValidationError(_(
                "Crie uma estágio."))

    state = fields.Selection(
        selection=[
            ("draft", "Transmitida"),
            ("confirm", "Emitida"),
            ("cancel", "Vencida"),
        ],
        string="Situação",
        readonly=True,
        copy=False,
        index=True,
        default="draft",
    )

    stage_id = fields.Many2one('contract.stage', string='Estágio',
            track_visibility='onchange',
            index=True, copy=False,
            default=lambda self: self._default_stage_id())

    def action_draft(self):
        self.write({"state": "draft"})

    def action_confirm(self):
        self.write({"state": "confirm"})

    def action_cancel(self):
        self.write({"state": "cancel"})
