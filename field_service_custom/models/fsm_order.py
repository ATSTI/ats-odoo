# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class FSMOrder(models.Model):
    _inherit = "fsm.order"

    loc_location = fields.Char(related="location_id.partner_id.contact_address", string="Endereço do Local")

    @api.onchange('person_id')
    def _onchange_person_id(self):
        if self.person_id:
            self.write({'person_ids': [(4, self.person_id.id)]})
            users = self.env['hr.employee']
            us = users.search([('name', '=', self.person_id.name)])
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
        if self.person_id.name not in self.name:
            name = ''
            for person in self.person_ids:
                if name == '':
                    name = f'{person.name} -'
                else:
                    name = f'{name} {person.name} -'
            self.name = f'{name} {self.name}'
        else:
            return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for va in vals_list:
            if_exists = self.env["fsm.order"].search([
                ('id', '!=', res.id),
                ('scheduled_date_start', '<=', res.scheduled_date_end),
                ('scheduled_date_end', '>=', res.scheduled_date_start),
            ])
            for ex in if_exists:
                for person in ex.person_ids:
                    for person2 in res.person_ids:
                        if person.id == person2.id:
                            raise UserError(_("Horário indisponível, já existe um evento agendado para este horário."))
        if res.person_id:
            name = ''
            for person in res.person_ids:
                if name == '':
                    name = f'{person.name} -'
                else:
                    name = f'{name} {person.name} -'
            res.name = f'{name} {res.name}'
        res._create_calendar_event()
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

        invoice_line_vals = []
        for cost in self.contractor_cost_ids:
            # DEPENDE DE QUAL O ID QUE VEM NA BASE, DEMO-MSM: 23
            if jrnl.id == 23:
                break
            price = price_list.get_product_price(
                product=cost.product_id,
                quantity=cost.quantity,
                partner=invoice_vals.get("partner_id"),
                date=False,
                uom_id=False,
            )
            template = cost.product_id.product_tmpl_id
            accounts = template.get_product_accounts()
            account = accounts["income"]
            taxes = template.taxes_id
            tax_ids = fpos.map_tax(taxes)
            invoice_line_vals.append(
                (
                    0,
                    0,
                    {
                        "product_id": cost.product_id.id,
                        "analytic_account_id": self.location_id.analytic_account_id.id,
                        "quantity": cost.quantity,
                        "name": cost.product_id.display_name,
                        "price_unit": price,
                        "account_id": account.id,
                        "fsm_order_ids": [(4, self.id)],
                        "tax_ids": [(6, 0, tax_ids.ids)],
                    },
                )
            )
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
        invoice.action_post()
        self.account_stage = "invoiced"
        return invoice

    def create_bills(self):
        vals = self.prepare_bills()
        fornecedor = self.env["account.move"].sudo().create(vals)
        fornecedor.invoice_date = datetime.now()
        fornecedor.action_post()
        return fornecedor