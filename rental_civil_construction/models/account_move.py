# Copyright (C) 2018, Open Source Integrators
# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    fsm_equipment_ids = fields.Many2many(
        "fsm.equipment",
        compute="_compute_fsm_equipment_ids",
        string="Field Service equipment associated to this invoice",
    )
    fsm_equipment_count = fields.Integer(
        string="FSM Equipment", compute="_compute_fsm_equipment_ids"
    )

    move_tag_ids = fields.Many2many(comodel_name="res.partner.category", related="partner_id.category_id", string="Marcadores")

    @api.depends("line_ids")
    def _compute_fsm_equipment_ids(self):
        for record in self:
            equipments = self.env["fsm.equipment"].search(
                [("invoice_lines", "in", record.line_ids.ids)]
            )
            record.fsm_equipment_ids = equipments
            record.fsm_equipment_count = len(record.fsm_equipment_ids)

    def action_view_fsm_equipments(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "fieldservice.action_fsm_dash_equipment"
        )
        if self.fsm_equipment_count > 1:
            action["domain"] = [("id", "in", self.fsm_equipment_ids.ids)]
        elif self.fsm_equipment_ids:
            action["views"] = [(self.env.ref("fieldservice.fsm_equipment_form").id, "form")]
            action["res_id"] = self.fsm_equipment_ids[0].id
        return action
