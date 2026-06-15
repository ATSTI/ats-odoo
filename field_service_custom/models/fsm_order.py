# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    loc_location = fields.Char(related="location_id.partner_id.contact_address", string="Endereço do Local")
    customer_address = fields.Char(
        string="Endereço",
        related="customer_id.contact_address",
        store=False
    )

    @api.onchange('person_id')
    def _onchange_person_id(self):
        if self.person_id:
            self.write({'person_ids': [(6, 0, [])]})
            self.write({'person_ids': [(4, self.person_id.id)]})
            users = self.env['hr.employee']
            us = users.search([('name', '=', self.person_id.name)])
            if len(us) > 1:
                raise UserError(_("Muitos funcionarios encontrados para o mesmo Usuario; Definições > Usuarios > Usuario escolhido > Funcionarios."))
            if us:
                vals_line = {
                    'employee_id': us.id,
                    'product_id': 39,
                }
                self.write({'employee_timesheet_ids': [(0, 0, vals_line)]})
            else:
                new_us = users.create({
                    'name': self.person_id.name,
                    'work_email': self.person_id.email,
                    'resource_calendar_id': self.person_id.calendar_id.id,
                    'work_location': self.person_id.location_ids.location_id.name,
                    'work_phone': self.person_id.phone,
                })
                vals_line = {
                    'employee_id': new_us.id,
                    'product_id': 39,
                }
                self.write({'employee_timesheet_ids': [(0, 0, vals_line)]})
            if self.employee_timesheet_ids:
                for line in self.employee_timesheet_ids:
                    line.name = f'{line.product_id.name}'
                    line.unit_amount = 1         

    def write(self, vals):
        res = super(FSMOrder, self).write(vals)
        for record in self:
            if "person_ids" in vals or "person_id" in vals:
                if record.person_ids:
                    parts = record.name.split(" - ")
                    old_name = parts[-1].strip() if parts else record.name
                    names = " - ".join(person.name for person in record.person_ids)
                    record.update({"name": f"{names} - {old_name}"})
            if "name" in vals and not "person_id" in vals:
                continue
            if "scheduled_date_start" in vals or "scheduled_date_end" in vals: #Esse ultimo para ter certeza que entra aqui quando duplica
                overlapping_orders = self.env["fsm.order"].search([
                    ('id', '!=', record.id),
                    ('scheduled_date_start', '<=', record.scheduled_date_end),
                    ('scheduled_date_end', '>=', record.scheduled_date_start),
                ])
                current_person_ids = set(record.person_ids.ids)
                for order in overlapping_orders:
                    if current_person_ids & set(order.person_ids.ids):  # interseção de conjuntos
                        raise UserError(_("Horário indisponível, já existe um evento agendado para este horário."))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        if res.person_ids:
            parts = res.name.split(" - ")
            old_name = parts[-1].strip() if parts else res.name
            names = " - ".join(person.name for person in res.person_ids)
            res.update({"name": f"{names} - {old_name}"})
        res._create_calendar_event()
        return res

    def prepare_bills(self):
        jrnl = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", "purchase"),
                ("active", "=", True),
            ],
            limit=1,
        )
        fpos = self.person_id.partner_id.property_account_position_id
        invoice_line_vals = []
        for cost in self.contractor_cost_ids:
            template = cost.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts["expense"]
            taxes = template.supplier_taxes_id
            tax_ids = fpos.map_tax(taxes)
            invoice_line_vals.append(
                (
                    0,
                    0,
                    {
                        "analytic_account_id": self.location_id.analytic_account_id.id,
                        "product_id": cost.product_id.id,
                        "quantity": cost.quantity,
                        "name": cost.product_id.display_name,
                        "price_unit": cost.price_unit,
                        "account_id": account.id,
                        "fsm_order_ids": [(4, self.id)],
                        "tax_ids": [(6, 0, tax_ids.ids)],
                    },
                )
            )
        vals = {
            "partner_id": self.person_id.partner_id.id,
            "move_type": "in_invoice",
            "journal_id": jrnl.id or False,
            "fiscal_position_id": fpos.id or False,
            "fsm_order_ids": [(4, self.id)],
            "company_id": self.env.company.id,
            "invoice_line_ids": invoice_line_vals,
        }
        if self.operating_unit_id:
            fiscal_vals = {
                "operating_unit_id": self.operating_unit_id.id,
                "document_type_id": 40, # 01 Nota Fiscal
                "fiscal_operation_id": self.company_id.sale_fiscal_operation_id.id,
            }
            vals.update(fiscal_vals)
        return vals
    
    def action_complete(self):
        res = super(FSMOrder, self).action_complete()
        for record in self:
            overlapping_orders = self.env["fsm.order"].search([
                ('id', '!=', record.id),
                ('scheduled_date_start', '<=', record.scheduled_date_end),
                ('scheduled_date_end', '>=', record.scheduled_date_start),
            ])
            current_person_ids = set(record.person_ids.ids)
            for order in overlapping_orders:
                if current_person_ids & set(order.person_ids.ids):  # interseção de conjuntos
                    raise UserError(_("Horário indisponível, já existe um evento agendado para este horário."))
            return res

    def account_prepare_invoice(self):
        jrnl = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", "sale"),
                ("active", "=", True),
            ],
            limit=1,
        )
        if self.bill_to == "contact":
            if not self.customer_id:
                raise ValidationError(_("Customer empty"))
            fpos = self.customer_id.property_account_position_id
            invoice_vals = {
                "partner_id": self.customer_id.id,
                "move_type": "out_invoice",
                "journal_id": jrnl.id or False,
                "fiscal_position_id": fpos.id or False,
                "fsm_order_ids": [(4, self.id)],
            }
            price_list = self.customer_id.property_product_pricelist

        else:
            fpos = self.location_id.customer_id.property_account_position_id
            invoice_vals = {
                "partner_id": self.location_id.customer_id.id,
                "move_type": "out_invoice",
                "journal_id": jrnl.id or False,
                "fiscal_position_id": fpos.id or False,
                "fsm_order_ids": [(4, self.id)],
                "company_id": self.env.company.id,
            }
            price_list = self.location_id.customer_id.property_product_pricelist

        if self.operating_unit_id:
            fiscal_vals = {
                "operating_unit_id": self.operating_unit_id.id,
                "document_type_id": 40, # 01 Nota Fiscal
                "fiscal_operation_id": self.company_id.sale_fiscal_operation_id.id,
            }
            invoice_vals.update(fiscal_vals)

        invoice_line_vals = []
        for line in self.employee_timesheet_ids:
            price = price_list.get_product_price(
                product=line.product_id,
                quantity=line.unit_amount,
                partner=invoice_vals.get("partner_id"),
                date=False,
                uom_id=False,
            )
            template = line.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts["income"]
            taxes = template.taxes_id
            tax_ids = fpos.map_tax(taxes)
            invoice_line_vals.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "analytic_account_id": line.account_id.id,
                        "quantity": line.unit_amount,
                        "name": line.name,
                        "price_unit": price,
                        "account_id": account.id,
                        "fsm_order_ids": [(4, self.id)],
                        "tax_ids": [(6, 0, tax_ids.ids)],
                    },
                )
            )
        invoice_vals.update({"invoice_line_ids": invoice_line_vals})
        return invoice_vals

    def account_create_invoice(self):
        invoice_vals = self.account_prepare_invoice()
        invoice = self.env["account.move"].sudo().create(invoice_vals)
        invoice.payment_reference = self.name
        # for line in invoice.invoice_line_ids:
        #     line.fiscal_operation_id = invoice.fiscal_operation_id.id
        #     line._onchange_product_id_fiscal()
        # invoice.action_post()
        self.account_stage = "invoiced"
        return invoice

    def create_bills(self):
        vals = self.prepare_bills()
        fornecedor = self.env["account.move"].sudo().create(vals)
        fornecedor.invoice_date = datetime.now()
        # fornecedor.action_post()
        return fornecedor

    def name_get(self):
        result = []
        for order in self:
            if order.location_id.partner_id and order.location_id.partner_id.name:
                display_name = order.location_id.partner_id.name
            else:
                display_name = 'Sem nome definido'
            result.append((order.id, display_name))
        return result