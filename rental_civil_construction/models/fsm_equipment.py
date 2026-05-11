from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta

ACCOUNT_STAGES = [
    ("draft", "Draft"),
    ("review", "Needs Review"),
    ("confirmed", "Confirmed"),
    ("invoiced", "Fully Invoiced"),
    ("no", "Nothing Invoiced"),
]

class FSMEquipment(models.Model):
    _inherit = 'fsm.equipment'

    date_rental_start = fields.Date(string='Data de Início da Locação')
    date_rental_end = fields.Date(string='Data de Término da Locação')

    product_id = fields.Many2one('product.product', string='Produto', required=True, domain="[('is_rental', '=', True)]")
    partner_id = fields.Many2one('res.partner', string='Parceiro', required=True)

    display_name_custom = fields.Char(string="Descrição")
    number_equipment = fields.Char(string='Número do Equipamento',)

    account_stage = fields.Selection(
        ACCOUNT_STAGES,
        compute="_compute_account_stage",
        store=True,
        string="Accounting Stage",
    )

    invoice_lines = fields.Many2many(
        "account.move.line",
        "fsm_equipment_account_move_line_rel",
        "fsm_equipment_id",
        "account_move_line_id",
        copy=False,
    )

    invoice_ids = fields.Many2many(
        "account.move",
        string="Invoices",
        compute="_compute_get_invoiced",
        readonly=True,
        copy=False,
    )

    invoice_count = fields.Integer(
        compute="_compute_get_invoiced",
        readonly=True,
        copy=False,
    )

    bill_invoice = fields.Boolean(string="Bill Invoice", default=False)
    customer_invoice = fields.Boolean(string="Customer Invoice", default=False)

    @api.depends("invoice_lines")
    def _compute_get_invoiced(self):
        for fsm in self:
            invoices = fsm.invoice_lines.mapped("move_id").filtered(
                lambda r: r.state != "cancel"
            )

            bill_invoices = invoices.filtered(lambda r: r.move_type == "in_invoice")
            customer_invoices = invoices.filtered(lambda r: r.move_type == "out_invoice")

            fsm.bill_invoice = bool(bill_invoices)
            fsm.customer_invoice = bool(customer_invoices)

            fsm.invoice_ids = invoices
            fsm.invoice_count = len(invoices)

    def action_view_invoices(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        invoices = self.mapped("invoice_ids")
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif invoices:
            action["views"] = [(self.env.ref("account.view_move_form").id, "form")]
            action["res_id"] = invoices.ids[0]
        return action

    @api.depends(
        "invoice_lines",
        "invoice_lines.move_id.state",
        "invoice_lines.move_id.move_type",
    )
    def _compute_account_stage(self):
        stage_concluido = self.env['fsm.stage'].search(
            [('name', 'ilike', 'Concluido')], limit=1
        )
        stage_faturar = self.env['fsm.stage'].search(
            [('name', 'ilike', 'Faturar')], limit=1
        )
        for fsm in self:
            invoices = fsm.invoice_lines.mapped("move_id").filtered(
                lambda r: r.state != "cancel"
            )
            has_bill = any(r.move_type == "in_invoice" for r in invoices)
            has_customer = any(r.move_type == "out_invoice" for r in invoices)

            if invoices and has_bill and has_customer:
                fsm.account_stage = "invoiced"
                fsm.stage_id = stage_concluido.id
            elif invoices:
                fsm.account_stage = "confirmed"
                fsm.stage_id = stage_faturar.id
            else:
                fsm.account_stage = "draft"
                fsm.stage_id = stage_faturar.id

    @api.onchange('date_rental_start')
    def _onchange_date_rental_start(self):
        if self.date_rental_start and self.product_id.rental_duration:
            self.date_rental_end = self.date_rental_start + timedelta(days=self.product_id.rental_duration)
    
    @api.constrains('date_rental_start', 'date_rental_end')
    def _check_rental_dates(self):
        for record in self:
            if record.date_rental_start and record.date_rental_end:
                if record.date_rental_start > record.date_rental_end:
                    raise UserError('A data de início da locação deve ser anterior à data de término.')          


    @api.constrains('product_id', 'number_equipment')
    def _check_number_equipment(self):
        for record in self:
            if not (record.product_id and record.number_equipment):
                continue

            excluded_stages = self.env['fsm.stage'].search([
                ('name', 'in', ['Trocas', 'Concluido', 'Cancelado'])
            ]).ids

            exists = self.search([
                ('id', '!=', record.id),
                ('stage_id', 'not in', excluded_stages),
                ('product_id', '=', record.product_id.id),
                ('number_equipment', '=', record.number_equipment)
            ], limit=1)

            if exists:
                raise ValidationError(
                    'Esse número de equipamento já está em uso para este produto.'
                )

    @api.onchange('product_id','number_equipment')
    def _onchange_display_name(self):
        for record in self:
            if record.product_id and record.number_equipment:
                record.display_name_custom = f"{record.product_id.name} - {record.number_equipment}"

    def write(self, vals):
        res = super().write(vals)
        return res    

    @api.model
    def create(self, vals):
        if vals.get('parent_id'):
            parent = self.browse(vals['parent_id'])

            # Só copie o que realmente precisa
            vals.setdefault('product_id', parent.product_id.id)
            vals.setdefault('partner_id', parent.partner_id.id)
            vals.setdefault('location_id', parent.location_id.id)

            # Stage específico para troca
            stage_trocas = self.env['fsm.stage'].search(
                [('name', '=', 'Trocas')], limit=1
            )
            if stage_trocas:
                vals['stage_id'] = stage_trocas.id

        if not vals.get('name') or vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('fsm.order')

        record = super().create(vals)

        return record
    

    def _get_journal(self, j_type):
        return self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", j_type),
                ("active", "=", True),
            ],
            limit=1,
        )


    def _prepare_invoice_lines(self, move_type):
        accounts = self.product_id.product_tmpl_id.get_product_accounts()

        account = (
            accounts["income"]
            if move_type == "out_invoice"
            else accounts["expense"]
        )

        qty = len(self.child_ids) + 1
        
        price_unit = (
            self.product_id.rental_price
            if move_type == "out_invoice"
            else self.calculate_owner_value()
        )

        return [
            (
                0,
                0,
                {
                    "product_id": self.product_id.id,
                    "quantity": 1,
                    "name": self.product_id.display_name,
                    "price_unit": price_unit,
                    "account_id": account.id,
                    "fsm_equipment_ids": [(4, self.id)],
                },
            )
            for _ in range(qty)
        ]

    def calculate_owner_value(self):
        if self.product_id.owner_value_type == 'percent':
            return (self.product_id.owner_value_rate / 100) * self.product_id.rental_price
        else:
            return self.product_id.owner_value_rate

    def prepare_bills(self):
        journal = self._get_journal("purchase")
        fpos = self.owned_by_id.property_account_position_id

        return {
            "partner_id": self.owned_by_id.id,
            "move_type": "in_invoice",
            "journal_id": journal.id or False,
            "fiscal_position_id": fpos.id or False,
            "fsm_equipment_ids": [(4, self.id)],
            "company_id": self.env.company.id,
            "user_id": self.managed_by_id.id or self.env.uid,
            "invoice_line_ids": self._prepare_invoice_lines("in_invoice"),
            "location_id": self.location_id.id,
        }

    def create_bills(self):
        self.ensure_one()

        bill_invoice = self.env['account.move'].search([
            ('fsm_equipment_ids', 'in', self.ids),
            ('move_type', '=', 'in_invoice'),
            ('state', 'not in', ['cancel', 'posted']),
            ('partner_id', '=', self.owned_by_id.id)
        ])

        if bill_invoice:
            vals = {
                'fsm_equipment_ids': [(4, self.id)],
                'invoice_line_ids': self._prepare_invoice_lines("in_invoice"),
            }
            bill_invoice.write(vals)
            return True

        return self.env["account.move"].create(self.prepare_bills())


    def account_prepare_invoice(self):
        journal = self._get_journal("sale")

        partner = self.partner_id or self.location_id.partner_id
        fpos = partner.property_account_position_id

        return {
            "partner_id": partner.id,
            "move_type": "out_invoice",
            "journal_id": journal.id or False,
            "fiscal_position_id": fpos.id or False,
            "fsm_order_ids": [(4, self.id)],
            "company_id": self.env.company.id,
            "user_id": self.managed_by_id.id or self.env.uid,
            "invoice_line_ids": self._prepare_invoice_lines("out_invoice"),
            "location_id": self.location_id.id,
        }


    def account_create_invoice(self):
        self.ensure_one()
        invoice = self.env["account.move"].create(
            self.account_prepare_invoice()
        )
        return invoice

    def account_no_invoice(self):
        self.account_stage = "no"

    