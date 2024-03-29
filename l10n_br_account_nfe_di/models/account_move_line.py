
from copy import deepcopy
from lxml import etree
from odoo import models, _, api, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    di_ids = fields.One2many(
        "declaracao.importacao",
        compute="_compute_di_ids",
        string='Delcaração de Importação (NT 2011/004)',
    )

    @api.depends("invoice_line_ids")
    def _compute_di_ids(self):
        di_ids = self.env["declaracao.importacao"].search([
            ("aml_id", "in", self.invoice_line_ids._ids)
        ])
        for record in self:
            record.di_ids = di_ids

    exp_ids = fields.One2many(
        "detalhe.exportacao",
        compute="_compute_exp_ids",
        string='Delcaração de Importação (NT 2011/004)',
    )

    @api.depends("invoice_line_ids")
    def _compute_exp_ids(self):
        exp_ids = self.env["detalhe.exportacao"].search([
            ("aml_id", "in", self.invoice_line_ids._ids)
        ])
        for record in self:
            record.exp_ids = exp_ids

    def button_wizard_di(self):
        for move in self:
            ctx = {
                'default_am_id': move.id,
                'di_id': 0,
            }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.create.di',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def button_wizard_detexp(self):
        for move in self:
            ctx = {
                'default_am_id': move.id,
                'di_id': 0,
            }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.create.detexp',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def button_copy_di(self):
        di = {}
        with_copy = []
        sequence_di = 0
        for record in self.di_ids:
            with_copy.append(record.aml_id.id)
            di["name"] = record.name
            di["date_registration"] = record.date_registration
            di["state_id"] = record.state_id.id
            di["location"] = record.location
            di["date_release"] = record.date_release
            di["type_transportation"] = record.type_transportation
            di["afrmm_value"] = record.afrmm_value
            di["tpIntermedio"] = record.tpIntermedio
            di["thirdparty_state_id"] = record.thirdparty_state_id.id
            di["thirdparty_cnpj"] = record.thirdparty_cnpj
            di["exporting_code"] = record.exporting_code
            di["company_id"] = record.company_id.id
            adicao = []
            for adic in record.adi_ids:
                vals = {}
                if adic.name:
                    vals["name"] = adic.name
                vals["manufacturer_code"] = adic.manufacturer_code
                vals["amount_discount"] = adic.amount_discount
                if adic.drawback_number:
                    vals["drawback_number"] = adic.drawback_number
                vals["company_id"] = adic.company_id.id
                sequence_di = adic.sequence_di
                adicao.append((0, 0, vals))
        sequence = 0
        for item in self.invoice_line_ids:
            if item.id in with_copy:
                continue
            if not sequence:
                sequence = sequence_di + 1
            else:
                sequence += 1
            adicao[0][2]['sequence_di'] = sequence  
            di["aml_id"] = item.id
            di["adi_ids"] = adicao
            declaracao = self.env["declaracao.importacao"].create(di)


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = [_name, "l10n_br_fiscal.document.line.mixin.methods"]
    _inherits = {"l10n_br_fiscal.document.line": "fiscal_document_line_id"}

    di_ids = fields.One2many(
        'declaracao.importacao',
        'aml_id',
        string='Delcaração de Importação (NT 2011/004)',
    )

    exp_ids = fields.One2many(
        'detalhe.exportacao',
        'aml_id',
        string='Detalhe da exportação',
        store=True, check_company=True,
    )

class DeclaracaoImportacao(models.Model):
    _name = 'declaracao.importacao'
    _description = "Declaração de Importação (NT 2011/004)"

    brl_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moeda",
        compute="_compute_brl_currency_id",
        default=lambda self: self.env.ref('base.BRL').id,
    )

    def _compute_brl_currency_id(self):
        for item in self:
            item.brl_currency_id = self.env.ref("base.BRL").id

    aml_id = fields.Many2one('account.move.line', string='Item',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="Linha da NFe.")
    name = fields.Char(string="Numero do Documento")
    date_registration = fields.Date('Data de Registro')
    state_id = fields.Many2one('res.country.state', 'UF desembaraço',domain="[('country_id.code', '=', 'BR')]")
    location = fields.Char('Local desembaraço', size=60)
    date_release = fields.Date('Data desembaraço') 
    type_transportation = fields.Selection([
        ('1', '1 - Marítima'),
        ('2', '2 - Fluvial'),
        ('3', '3 - Lacustre'),
        ('4', '4 - Aérea'),
        ('5', '5 - Postal'),
        ('6', '6 - Ferroviária'),
        ('7', '7 - Rodoviária'),
        ('8', '8 - Conduto / Rede Transmissão'),
        ('9', '9 - Meios Próprios'),
        ('10', '10 - Entrada / Saída ficta'),
    ], 'Via transporte internacional',default="1")
    afrmm_value = fields.Monetary(
        'Valor da AFRMM', 
        currency_field="brl_currency_id")
    tpIntermedio = fields.Selection([
        ('1', '1 - Importação por conta própria'),
        ('2', '2 - Importação por conta e ordem'),
        ('3', '3 - Importação por encomenda'),
    ], 'Forma Importação', default='1')
    thirdparty_cnpj = fields.Char('CNPJ adquir./encomendante', size=18)
    thirdparty_state_id = fields.Many2one(
        'res.country.state', 'UF adquir./encomendante',
        domain="[('country_id.code', '=', 'BR')]")
    exporting_code = fields.Char('Código do Exportador', size=60)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=lambda s: s.env.company)
    adi_ids = fields.One2many(
        'declaracao.adicao',
        'di_id',
        string='Adições (NT 2011/004',
        store=True, check_company=True, copy=True,
        )

    def edit_di(self):
        adi = {}
        adi_id = 0
        for line in self.adi_ids:
            adi['nAdicao'] = line.name
            adi['nSeqAdic'] = line.sequence_di
            adi['cFabricante'] = line.manufacturer_code
            adi['vDescDI'] = line.amount_discount
            adi['nDraw'] = line.drawback_number
            adi_id = line.id
            adi['company_id'] = line.company_id
        ctx = {
            'default_nfe40_nDI': self.name,
            'default_nfe40_dDI': self.date_registration,
            'default_nfe40_xLocDesemb': self.location,
            'default_nfe40_UFDesemb': self.state_id.id,
            'default_nfe40_tpViaTransp': self.type_transportation,
            'default_nfe40_vAFRMM': self.afrmm_value,
            'default_nfe40_tpIntermedio': self.tpIntermedio,
            'default_nfe40_CNPJ': self.thirdparty_cnpj,
            'default_nfe40_UFTerceiro': self.thirdparty_state_id.id,
            'default_nfe40_cExportador': self.exporting_code,
            'default_company_id': self.company_id.id,
            'default_nfe40_dDesemb': self.date_release,
            'adi': adi,
            'default_aml_id': self.aml_id.id,
            'di_id': self.id,
            'adi_id': adi_id,
            'default_am_id': self.aml_id.move_id.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.create.di',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class DeclaracaoAdicao(models.Model):
    _name = 'declaracao.adicao'
    _description = "Adições (NT 2011/004)"

    di_id = fields.Many2one('declaracao.importacao', string='DI',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="Declaração de importação (DI).")
    brl_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Moeda",
        compute="_compute_brl_currency_id",
        default=lambda self: self.env.ref('base.BRL').id,
    )

    def _compute_brl_currency_id(self):
        for item in self:
            item.brl_currency_id = self.env.ref("base.BRL").id

    name = fields.Char('Número da Adição', size=3)
    sequence_di = fields.Integer('Número sequencial', default=1, required=True)
    manufacturer_code = fields.Char('Código fabricante', size=60, required=True)
    amount_discount = fields.Monetary(string='Valor desconto', currency_field="brl_currency_id", required=True)
    drawback_number = fields.Char('Número Drawback', size=11)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=lambda s: s.env.company)


class DetalheExportacao(models.Model):
    _name = "detalhe.exportacao"
    _description = "Detalhe da exportação"

    aml_id = fields.Many2one('account.move.line', string='Item',
        index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
        check_company=True,
        help="Linha da NFe.")
    name = fields.Char('Número Drawback', size=20)
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=lambda s: s.env.company)
    # exportind_ids = fields.Many2one(
    #     'export.ind',
    #     string='Exportação indireta',
    # )
    registro_exp = fields.Char('Registro exportação')
    chava_nfe = fields.Char('Chave NF-e rec.')
    q_export = fields.Float(
        'Quantidade exportado', 
    )

    def edit_detexp(self):
        ctx = {
            'default_nfe40_nDraw': self.name,
            'default_nfe40_nRE': self.registro_exp,
            'default_nfe40_chNFe': self.chava_nfe,
            'default_nfe40_qExport': self.q_export,
            'default_company_id': self.company_id.id,
            'default_aml_id': self.aml_id.id,
            'detexp_id': self.id,
            'default_am_id': self.aml_id.move_id.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.create.detexp',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

# class ExportInd(models.Model):
#     _name = "export.ind"
#     _description = "Exportação indireta"
#     _rec_name = "registro_exp"



class AccountMoveLineMethods(models.AbstractModel):
    _inherit = "l10n_br_fiscal.document.line.mixin.methods"
    
    @api.depends('journal_id')
    def _compute_company_id(self):
        for move in self:
            move.company_id = move.journal_id.company_id or move.company_id or self.env.company


 