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

    date_rental_start = fields.Date(
        string='Data de Início da Locação', 
        required=True, 
        default=lambda self: fields.Date.today() + timedelta(days=1)
    )
    date_rental_end = fields.Date(string='Data de Término da Locação')

    product_id = fields.Many2one('product.product', string='Produto', required=True, domain="[('is_rental', '=', True)]")
    partner_id = fields.Many2one('res.partner', string='Parceiro', required=True)

    display_name_custom = fields.Char(string="Descrição")
    number_equipment = fields.Char(string='Número do Equipamento')

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

    @api.onchange('date_rental_start')
    def _onchange_date_rental_start(self):
        if self.date_rental_start and self.product_id.rental_duration:
            self.date_rental_end = self.date_rental_start + timedelta(days=self.product_id.rental_duration)
        if (
            self.date_rental_start <= fields.Date.today() 
            and self.date_rental_end >= fields.Date.today()
            and not (self.stage_id.name in ['À FATURAR', 'CONCLUIDO', 'CANCELADO'])
        ):
            self.stage_id = self.env['fsm.stage'].search([('name', 'ilike', 'Em Locação')], limit=1).id
        elif (
            (self.date_rental_start > fields.Date.today()
            or self.date_rental_end < fields.Date.today()) 
            and not (self.stage_id.name in ['À FATURAR', 'CONCLUIDO', 'CANCELADO'])
        ):
            self.stage_id = self.env['fsm.stage'].search([('name', 'ilike', 'Novo')], limit=1).id

    
    @api.constrains('date_rental_start', 'date_rental_end')
    def _check_rental_dates(self):
        for record in self:
            if record.date_rental_start and record.date_rental_end:
                if record.date_rental_start > record.date_rental_end:
                    raise UserError('A data de início da locação deve ser anterior à data de término.')
                else:
                    record._check_number_equipment()


    @api.constrains('product_id', 'number_equipment')
    def _check_number_equipment(self):
        for record in self:
            if not (record.product_id and record.number_equipment):
                continue

            excluded_stages = self.env['fsm.stage'].search([
                ('name', 'in', ['À Faturar', 'Concluido', 'Cancelado'])
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
            else:
                self._onchange_display_name()

    @api.onchange('product_id', 'number_equipment')
    def _onchange_display_name(self):
        # 1. Atualização do display_name_custom
        if self.product_id and self.number_equipment:
            self.display_name_custom = f"{self.product_id.name} - {self.number_equipment}"

        # 2. Histórico nas notas
        if self._origin.number_equipment != self.number_equipment:
            dt_start = self.date_rental_start.strftime('%d/%m/%Y') if self.date_rental_start else ''
            dt_end = self.date_rental_end.strftime('%d/%m/%Y') if self.date_rental_end else ''
            product_name = self.product_id.name or ''

            # Estilos CSS Inline reutilizáveis
            table_style = "width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 8px; font-family: sans-serif; font-size: 13px;"
            th_style = "border: 1px solid #d1d5db; background-color: #f3f4f6; color: #374151; padding: 8px 12px; text-align: left; font-weight: 600;"
            td_style = "border: 1px solid #d1d5db; padding: 8px 12px; color: #4b5563;"

            if not self.notes:
                header = (
                    f'<table style="{table_style}">'
                    '<thead>'
                    '<tr>'
                    f'<th style="{th_style}">Produto</th>'
                    f'<th style="{th_style}">Número do Equipamento</th>'
                    f'<th style="{th_style}">Data de Início</th>'
                    f'<th style="{th_style}">Data de Término</th>'
                    '</tr>'
                    '</thead>'
                    '<tbody>'
                )
                base_notes = header
            else:
                base_notes = self.notes.replace("</tbody></table>", "").replace("</table>", "")

            row = (
                '<tr>'
                f'<td style="{td_style}">{product_name}</td>'
                f'<td style="{td_style}">{self.number_equipment or ""}</td>'
                f'<td style="{td_style}">{dt_start}</td>'
                f'<td style="{td_style}">{dt_end}</td>'
                '</tr>'
            )

            self.notes = f"{base_notes}{row}</tbody></table>"

    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            "name": "",
            "number_equipment": False,
            "notes": False,
        })
        return super().copy(default)

    @api.model
    def create(self, vals):
        # Em Desuso
        if vals.get('parent_id'):
            parent = self.browse(vals['parent_id'])

            # Só copie o que realmente precisa
            vals.setdefault('product_id', parent.product_id.id)
            vals.setdefault('partner_id', parent.partner_id.id)
            vals.setdefault('location_id', parent.location_id.id)

            # Stage específico para troca
            stage_trocas = self.env['fsm.stage'].search(
                [('name', 'ilike', 'Trocas')], limit=1
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

    def _extract_items_from_html(self):
        self.ensure_one()
        if not self.notes:
            return []

        # 1. Isolamos o conteúdo da tag <tbody>
        if '<tbody>' in self.notes and '</tbody>' in self.notes:
            tbody_content = self.notes.split('<tbody>')[1].split('</tbody>')[0]
        else:
            tbody_content = self.notes

        # 2. Separamos por linhas <tr>
        tr_blocks = tbody_content.split('<tr>')
        items = []

        for tr in tr_blocks:
            if '</tr>' not in tr:
                continue
            
            row_html = tr.split('</tr>')[0]
            
            # Extraímos o texto entre as tags <td>...</td>
            td_blocks = row_html.split('<td')
            cols = []
            for td in td_blocks:
                if '</td>' in td:
                    # Remove o fechamento e limpa estilos/propriedades da tag
                    if not td.split('>')[-1]:
                        val = td.split('>')[--1]
                    val = val.split('</td')[0].strip()
                    cols.append(val)

            # Estrutura esperada da tabela: [Produto, Num Equipamento, Data Inicio, Data Termino]
            if len(cols) >= 4:
                items.append({
                    'product_name': cols[0],
                    'number_equipment': cols[1],
                    'date_start': cols[2],
                    'date_end': cols[3],
                })

        return items

    def _prepare_invoice_lines(self, move_type):
        self.ensure_one()
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        
        account = (
            accounts["income"]
            if move_type == "out_invoice"
            else accounts["expense"]
        )
        price_unit = (
            self.product_id.rental_price
            if move_type == "out_invoice"
            else self.calculate_owner_value()
        )

        invoice_line = []

        # 1. Extrai todos os itens gravados na tabela HTML
        html_items = self._extract_items_from_html()

        # 2. Itera sobre cada linha da tabela HTML para montar a fatura
        for item in html_items:
            dt_start = item['date_start']
            dt_end = item['date_end']
            num_eq = f" ({item['number_equipment']})" if item['number_equipment'] else ""

            # Descrição formatada da linha
            description = f"{dt_start} - {dt_end}{num_eq}" if (dt_start or dt_end) else item['product_name']

            invoice_line.append((0, 0, {
                "product_id": self.product_id.id,
                "quantity": 1,
                "name": description,
                "price_unit": price_unit,
                "account_id": account.id,
                "fsm_equipment_ids": [(4, self.id)],
                "location_id": self.location_id.id if self.location_id else False,
            }))

        return invoice_line

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
            "narration": self.notes,
        }


    def account_create_invoice(self):
        self.ensure_one()

        # Se já existir uma fatura aberta para o mesmo local, juntar na mesma
        exist_inv = self.env["account.move"].search([
            ('partner_id', '=', self.partner_id.id),
            ('move_type', '=', "out_invoice"),
        ])
        for inv in exist_inv:
            if any(line.location_id == self.location_id for line in inv.invoice_line_ids):
                inv.write({
                    'invoice_line_ids': self._prepare_invoice_lines("out_invoice"),
                })
                return inv
            
        invoice = self.env["account.move"].create(
            self.account_prepare_invoice()
        )
        return invoice

    def account_no_invoice(self):
        self.account_stage = "no"

class FSMLocation(models.Model):
    _inherit = "fsm.location"

    def zip_search(self):
        return self.env["l10n_br.zip"].zip_search(self)