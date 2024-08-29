# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

class BrAccountCFOP(models.Model):
    """CFOP - Código Fiscal de Operações e Prestações"""
    _name = 'br_account.cfop'
    _description = 'CFOP'

    code = fields.Char(u'Código', size=4, required=True)
    name = fields.Char('Nome', size=256, required=True)
    small_name = fields.Char('Nome Reduzido', size=32, required=True)
    description = fields.Text(u'Descrição')
    type = fields.Selection([('input', u'Entrada'),
                             ('output', u'Saída')],
                            'Tipo', required=True)
    parent_id = fields.Many2one(
        'br_account.cfop', 'CFOP Pai')
    child_ids = fields.One2many(
        'br_account.cfop', 'parent_id', 'CFOP Filhos')
    internal_type = fields.Selection(
        [('view', u'Visualização'), ('normal', 'Normal')],
        'Tipo Interno', required=True, default='normal')

    _sql_constraints = [
        ('br_account_cfop_code_uniq', 'unique (code)',
            u'Já existe um CFOP com esse código !')
    ]

class BrAccountServiceType(models.Model):
    _name = 'br_account.service.type'
    _description = u'Cadastro de Operações Fiscais de Serviço'

    code = fields.Char(u'Código', size=16, required=True)
    name = fields.Char(u'Descrição', size=256, required=True)
    parent_id = fields.Many2one(
        'br_account.service.type', u'Tipo de Serviço Pai')
    child_ids = fields.One2many(
        'br_account.service.type', 'parent_id',
        u'Tipo de Serviço Filhos')
    internal_type = fields.Selection(
        [('view', u'Visualização'), ('normal', 'Normal')], 'Tipo Interno',
        required=True, default='normal')
    federal_nacional = fields.Float(u'Imposto Fed. Sobre Serviço Nacional')
    federal_importado = fields.Float(u'Imposto Fed. Sobre Serviço Importado')
    estadual_imposto = fields.Float(u'Imposto Estadual')
    municipal_imposto = fields.Float(u'Imposto Municipal')

class BrAccountFiscalDocument(models.Model):
    _name = 'br_account.fiscal.document'
    _description = 'Tipo de Documento Fiscal'

    code = fields.Char(u'Codigo', size=8, required=True)
    name = fields.Char(u'Descrição', size=64)
    electronic = fields.Boolean(u'Eletrônico')
    nfse_eletronic = fields.Boolean('Emite NFS-e?')


class BrAccountDocumentSerie(models.Model):
    _name = 'br_account.document.serie'
    _description = u'Série de documentos fiscais'

    code = fields.Char(u'Código', size=3, required=True)
    name = fields.Char(u'Descrição', required=True)
    active = fields.Boolean('Ativo')
    fiscal_type = fields.Selection([('service', u'Serviço'),
                                    ('product', 'Produto')], 'Tipo Fiscal',
                                   default='service')
    fiscal_document_id = fields.Many2one('br_account.fiscal.document',
                                         'Documento Fiscal', required=True)
    company_id = fields.Many2one('res.company', 'Empresa',
                                 required=True)
    internal_sequence_id = fields.Many2one('ir.sequence',
                                           u'Sequência Interna')

class BrAccountCNAE(models.Model):
    _name = 'br_account.cnae'
    _description = 'Cadastro de CNAE'

    code = fields.Char(u'Código', size=16, required=True)
    name = fields.Char(u'Descrição', size=64, required=True)
    version = fields.Char(u'Versão', size=16, required=True)
    parent_id = fields.Many2one('br_account.cnae', 'CNAE Pai')
    child_ids = fields.One2many(
        'br_account.cnae', 'parent_id', 'CNAEs Filhos')
    internal_type = fields.Selection(
        [('view', u'Visualização'), ('normal', 'Normal')],
        'Tipo Interno', required=True, default='normal')

class ImportDeclaration(models.Model):
    _name = 'import.declaration'
    _description = "Declaração de Importação"

    invoice_id = fields.Many2one(
        'account.invoice', 'Fatura',
        ondelete='cascade', index=True)

    name = fields.Char(u'Número da DI', size=10, required=True)
    date_registration = fields.Date(u'Data de Registro', required=True)
    state_id = fields.Many2one(
        'res.country.state', u'Estado',
        domain="[('country_id.code', '=', 'BR')]", required=True)
    location = fields.Char(u'Local', required=True, size=60)
    date_release = fields.Date(u'Data de Liberação', required=True)
    type_transportation = fields.Selection([
        ('1', u'1 - Marítima'),
        ('2', u'2 - Fluvial'),
        ('3', u'3 - Lacustre'),
        ('4', u'4 - Aérea'),
        ('5', u'5 - Postal'),
        ('6', u'6 - Ferroviária'),
        ('7', u'7 - Rodoviária'),
        ('8', u'8 - Conduto / Rede Transmissão'),
        ('9', u'9 - Meios Próprios'),
        ('10', u'10 - Entrada / Saída ficta'),
    ], u'Transporte Internacional', required=True, default="1")
    afrmm_value = fields.Float(
        'Valor da AFRMM', digits=dp.get_precision('Account'), default=0.00)
    type_import = fields.Selection([
        ('1', u'1 - Importação por conta própria'),
        ('2', u'2 - Importação por conta e ordem'),
        ('3', u'3 - Importação por encomenda'),
    ], u'Tipo de Importação', default='1', required=True)
    thirdparty_cnpj = fields.Char('CNPJ', size=18)
    thirdparty_state_id = fields.Many2one(
        'res.country.state', u'Estado',
        domain="[('country_id.code', '=', 'BR')]")
    exporting_code = fields.Char(
        u'Código do Exportador', required=True, size=60)
    line_ids = fields.One2many(
        'br_account.import.declaration.line',
        'import_declaration_id', 'Linhas da DI')
    invoice_eletronic_line_id = fields.Many2one(
        'br_odoo.nfe.item', u'Linha de Documento Eletrônico',
        ondelete='cascade', index=True)


class ImportDeclarationLine(models.Model):
    _name = 'br_account.import.declaration.line'
    _description = "Linha da declaração de importação"

    import_declaration_id = fields.Many2one(
        'br_account.import.declaration', u'DI', ondelete='cascade')
    sequence = fields.Integer(u'Sequência', default=1, required=True)
    name = fields.Char(u'Adição', size=3, required=True)
    manufacturer_code = fields.Char(
        u'Código do Fabricante', size=60, required=True)
    amount_discount = fields.Float(
        string=u'Valor', digits=dp.get_precision('Account'), default=0.00)
    drawback_number = fields.Char(u'Número Drawback', size=11)
    invoice_line_id = fields.Many2one(
        'account.invoice.line',
        string="Linhas da fatura")


class AccountDocumentRelated(models.Model):
    _name = 'br_account.document.related'
    _description = "Documentos Relacionados"

    invoice_id = fields.Many2one('account.invoice', 'Documento Fiscal',
                                 ondelete='cascade')
    invoice_related_id = fields.Many2one(
        'account.invoice', 'Documento Fiscal', ondelete='cascade')
    document_type = fields.Selection(
        [('nf', 'NF'), ('nfe', 'NF-e'), ('cte', 'CT-e'),
            ('nfrural', 'NF Produtor'), ('cf', 'Cupom Fiscal')],
        'Tipo Documento', required=True)
    access_key = fields.Char('Chave de Acesso', size=44)
    serie = fields.Char(u'Série', size=12)
    internal_number = fields.Char(u'Número', size=32)
    state_id = fields.Many2one('res.country.state', 'Estado',
                               domain="[('country_id.code', '=', 'BR')]")
    cnpj_cpf = fields.Char('CNPJ/CPF', size=18)
    cpfcnpj_type = fields.Selection(
        [('cpf', 'CPF'), ('cnpj', 'CNPJ')], 'Tipo Doc.',
        default='cnpj')
    inscr_est = fields.Char('Inscr. Estadual/RG', size=16)
    date = fields.Date('Data')
    fiscal_document_id = fields.Many2one(
        'br_account.fiscal.document', 'Documento')
    invoice_eletronic_id = fields.Many2one(
        'br_odoo.nfe', u'Documento Eletrônico', ondelete='cascade')


class BrAccountFiscalObservation(models.Model):
    _name = 'br_account.fiscal.observation'
    _description = u'Mensagen Documento Eletrônico'
    _order = 'sequence'

    sequence = fields.Integer(u'Sequência', default=1, required=True)
    name = fields.Char(u'Descrição', required=True, size=50)
    message = fields.Text(u'Mensagem', required=True)
    tipo = fields.Selection([('fiscal', 'Observação Fiscal'),
                             ('observacao', 'Observação')], string=u"Tipo")
    document_id = fields.Many2one(
        'br_account.fiscal.document', string="Documento Fiscal")


class BrAccountCategoriaFiscal(models.Model):
    _name = 'br_account.fiscal.category'
    _description = 'Categoria Fiscal'

    name = fields.Char('Descrição', required=True)