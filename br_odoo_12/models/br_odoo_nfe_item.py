# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from .cst import CST_ICMS
from .cst import CSOSN_SIMPLES
from .cst import CST_IPI
from .cst import CST_PIS_COFINS
from .cst import ORIGEM_PROD

STATE = {'edit': [('readonly', False)]}


class BrOdooNfeItem(models.Model):
    _name = 'br.odoo.nfe.item'
    _description = "Item da nota fiscal eletrônica"

    name = fields.Text(u'Nome', readonly=True, states=STATE)
    company_id = fields.Many2one(
        'res.company', u'Empresa', index=True, readonly=True, states=STATE)
    invoice_eletronic_id = fields.Many2one(
        'invoice.eletronic', string=u'Documento', readonly=True, states=STATE)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Company Currency")
    state = fields.Selection(
        related='invoice_eletronic_id.state', string="State")

    product_id = fields.Many2one(
        'product.product', string=u'Produto', readonly=True, states=STATE)
    tipo_produto = fields.Selection(
        [('product', 'Produto'),
         ('service', u'Serviço')],
        string="Tipo Produto", readonly=True, states=STATE)
    cfop = fields.Char(u'CFOP', size=5, readonly=True, states=STATE)
    ncm = fields.Char(u'NCM', size=10, readonly=True, states=STATE)

    uom_id = fields.Many2one(
        'uom.uom', string=u'Unidade Medida', readonly=True, states=STATE)
    quantidade = fields.Float(
        string=u'Quantidade', readonly=True, states=STATE,
        digits=dp.get_precision('Product Unit of Measure'))
    preco_unitario = fields.Monetary(
        string=u'Preço Unitário', digits=dp.get_precision('Product Price'),
        readonly=True, states=STATE)

    pedido_compra = fields.Char(
        string="Pedido Compra", size=60,
        help="Se setado aqui sobrescreve o pedido de compra da fatura")
    item_pedido_compra = fields.Char(
        string="Item de compra", size=20,
        help=u'Item do pedido de compra do cliente')

    frete = fields.Monetary(
        string=u'Frete', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    seguro = fields.Monetary(
        string=u'Seguro', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    desconto = fields.Monetary(
        string=u'Desconto', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    outras_despesas = fields.Monetary(
        string=u'Outras despesas', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    tributos_estimados = fields.Monetary(
        string=u'Valor Estimado Tributos', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    valor_bruto = fields.Monetary(
        string=u'Valor Bruto', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    valor_liquido = fields.Monetary(
        string=u'Valor Líquido', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    indicador_total = fields.Selection(
        [('0', u'0 - Não'), ('1', u'1 - Sim')],
        string=u"Compõe Total da Nota?", default='1',
        readonly=True, states=STATE)

    origem = fields.Selection(
        ORIGEM_PROD, string=u'Origem Mercadoria', readonly=True, states=STATE)
    icms_cst = fields.Selection(
        CST_ICMS + CSOSN_SIMPLES, string=u'Situação Tributária',
        readonly=True, states=STATE)
    icms_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_tipo_base = fields.Selection(
        [('0', u'0 - Margem Valor Agregado (%)'),
         ('1', u'1 - Pauta (Valor)'),
         ('2', u'2 - Preço Tabelado Máx. (valor)'),
         ('3', u'3 - Valor da operação')],
        string=u'Modalidade BC do ICMS', readonly=True, states=STATE)
    icms_base_calculo = fields.Monetary(
        string=u'Base de cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_aliquota_reducao_base = fields.Float(
        string=u'% Redução Base', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_valor_credito = fields.Monetary(
        string=u"Valor de Cŕedito", digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_aliquota_credito = fields.Float(
        string=u'% de Crédito', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    icms_st_tipo_base = fields.Selection(
        [('0', u'0- Preço tabelado ou máximo  sugerido'),
         ('1', u'1 - Lista Negativa (valor)'),
         ('2', u'2 - Lista Positiva (valor)'),
         ('3', u'3 - Lista Neutra (valor)'),
         ('4', u'4 - Margem Valor Agregado (%)'), ('5', '5 - Pauta (valor)')],
        string='Tipo Base ICMS ST', required=True, default='4',
        readonly=True, states=STATE)
    icms_st_aliquota_mva = fields.Float(
        string=u'% MVA', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_st_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_st_base_calculo = fields.Monetary(
        string=u'Base de cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_st_aliquota_reducao_base = fields.Float(
        string=u'% Redução Base', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_st_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    icms_aliquota_diferimento = fields.Float(
        string=u'% Diferimento', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    icms_valor_diferido = fields.Monetary(
        string=u'Valor Diferido', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    icms_motivo_desoneracao = fields.Char(
        string=u'Motivo Desoneração', size=2, readonly=True, states=STATE)
    icms_valor_desonerado = fields.Monetary(
        string=u'Valor Desonerado', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ----------- IPI -------------------
    ipi_cst = fields.Selection(CST_IPI, string=u'Situação tributária')
    ipi_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ipi_base_calculo = fields.Monetary(
        string=u'Base de cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ipi_reducao_bc = fields.Float(
        string=u'% Redução Base', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ipi_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ----------- II ----------------------
    ii_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ii_aliquota = fields.Float(
        string=u'Alíquota II', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ii_valor_despesas = fields.Monetary(
        string=u'Despesas Aduaneiras', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ii_valor = fields.Monetary(
        string=u'Imposto de Importação', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    ii_valor_iof = fields.Monetary(
        string=u'IOF', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ------------ PIS ---------------------
    pis_cst = fields.Selection(
        CST_PIS_COFINS, string=u'Situação Tributária',
        readonly=True, states=STATE)
    pis_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    pis_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    pis_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    pis_valor_retencao = fields.Monetary(
        string=u'Valor Retido', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ------------ COFINS ------------
    cofins_cst = fields.Selection(
        CST_PIS_COFINS, string=u'Situação Tributária',
        readonly=True, states=STATE)
    cofins_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    cofins_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    cofins_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    cofins_valor_retencao = fields.Monetary(
        string=u'Valor Retido', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ----------- ISSQN -------------
    issqn_codigo = fields.Char(
        string=u'Código', size=10, readonly=True, states=STATE)
    issqn_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    issqn_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    issqn_valor = fields.Monetary(
        string=u'Valor Total', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    issqn_valor_retencao = fields.Monetary(
        string=u'Valor Retenção', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    # ------------ RETENÇÔES ------------
    csll_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    csll_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    csll_valor_retencao = fields.Monetary(
        string=u'Valor Retenção', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    irrf_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    irrf_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    irrf_valor_retencao = fields.Monetary(
        string=u'Valor Retenção', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    inss_base_calculo = fields.Monetary(
        string=u'Base de Cálculo', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    inss_aliquota = fields.Float(
        string=u'Alíquota', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)
    inss_valor_retencao = fields.Monetary(
        string=u'Valor Retenção', digits=dp.get_precision('Account'),
        readonly=True, states=STATE)

    account_invoice_line_id = fields.Many2one(
        string="Account Invoice Line",
        comodel_name="account.invoice.line",
        )

    cst_danfe = fields.Char(string="CST Danfe", compute="_compute_cst_danfe")

    cest = fields.Char(string="CEST", size=10, readonly=True, states=STATE,
                       help=u"Código Especificador da Substituição Tributária")
    classe_enquadramento_ipi = fields.Char(
        string="Classe Enquadramento", size=5, readonly=True, states=STATE)
    codigo_enquadramento_ipi = fields.Char(
        string="Classe Enquadramento", size=3, default='999',
        readonly=True, states=STATE)

    import_declaration_ids = fields.One2many(
        'import.declaration' ,
        'invoice_eletronic_line_id', string=u'Declaração de Importação')

    # ----------- ICMS INTERESTADUAL -----------
    tem_difal = fields.Boolean(string=u'Difal?', readonly=True, states=STATE)
    icms_bc_uf_dest = fields.Monetary(
        string=u'Base ICMS', readonly=True, states=STATE)
    icms_aliquota_fcp_uf_dest = fields.Float(
        string=u'% FCP', readonly=True, states=STATE)
    icms_aliquota_uf_dest = fields.Float(
        string=u'% ICMS destino', readonly=True, states=STATE)
    icms_aliquota_interestadual = fields.Float(
        string=u"% ICMS Inter", readonly=True, states=STATE)
    icms_aliquota_inter_part = fields.Float(
        string=u'% Partilha', default=100.0, readonly=True, states=STATE)
    icms_uf_remet = fields.Monetary(
        string=u'ICMS Remetente', readonly=True, states=STATE)
    icms_uf_dest = fields.Monetary(
        string=u'ICMS Destino', readonly=True, states=STATE)
    icms_fcp_uf_dest = fields.Monetary(
        string=u'Valor FCP', readonly=True, states=STATE)
    informacao_adicional = fields.Text(string=u"Informação Adicional")

    # =========================================================================
    # ICMS Retido anteriormente por ST
    # =========================================================================
    icms_substituto = fields.Monetary(
        "ICMS Substituto", readonly=True, states=STATE)
    icms_bc_st_retido = fields.Monetary(
        "Base Calc. ST Ret.", readonly=True, states=STATE)
    icms_aliquota_st_retido = fields.Float(
        "% ST Retido", readonly=True, states=STATE)
    icms_st_retido = fields.Monetary(
        "ICMS ST Ret.", readonly=True, states=STATE)
