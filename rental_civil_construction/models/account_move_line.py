# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    fsm_equipment_ids = fields.Many2many(
        "fsm.equipment",
        "fsm_equipment_account_move_line_rel",
        "account_move_line_id",
        "fsm_equipment_id",
        string="FSM equipments",
        readonly=True,
        copy=False,
    )

    location_id = fields.Many2one(
        "fsm.location",
        string="Location",
    )
