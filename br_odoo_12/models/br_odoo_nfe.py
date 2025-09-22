# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _


STATE = {'edit': [('readonly', False)]}

class BrOdooNfe(models.Model):
    _name = 'br_odoo.nfe'
    _description = "Nota Fiscal"
    _order = 'id desc'

    code = fields.Char(
        'Código', size=100, required=True, readonly=True, states=STATE)
    name = fields.Char(
        'Nome', size=100, required=True, readonly=True, states=STATE)
    company_id = fields.Many2one(
        'res.company', 'Empresa', readonly=True, states=STATE)
    state = fields.Selection(
        [('draft', 'Provisório'),
         ('edit', 'Editar'),
         ('error', 'Erro'),
         ('done', 'Enviado'),
         ('cancel', 'Cancelado'),
         ('denied', 'Denegado')],
        string='State', default='draft', readonly=True, states=STATE,
        tracking=True)
    schedule_user_id = fields.Many2one(
        'res.users', string="Agendado por", readonly=True,
        tracking=True)
    tipo_operacao = fields.Selection(
        [('entrada', 'Entrada'),
         ('saida', 'Saída')],
        string='Tipo de Operação', readonly=True, states=STATE)
    model = fields.Selection(
        [('55', '55 - NFe'),
         ('65', '65 - NFCe'),
         ('001', 'NFS-e - Nota Fiscal Paulistana'),
         ('002', 'NFS-e - Provedor GINFES'),
         ('008', 'NFS-e - Provedor SIMPLISS'),
         ('009', 'NFS-e - Provedor SUSES'),
         ('010', 'NFS-e Imperial - Petrópolis'),
         ('012', 'NFS-e - Florianópolis')],
        string='Modelo', readonly=True, states=STATE)
    serie = fields.Integer(string='Série',)
    serie_documento = fields.Char(string='Série Documento', size=6)
    numero = fields.Integer(
        string='Número', readonly=True, states=STATE)
    numero_controle = fields.Integer(
        string='Número de Controle', readonly=True, states=STATE)
    data_agendada = fields.Date(
        string='Data agendada',
        readonly=True,
        default=fields.Date.today,
        states=STATE)
    data_emissao = fields.Datetime(
        string='Data emissão', readonly=True, states=STATE)
    data_autorizacao = fields.Char(
        string='Data de autorização', size=30, readonly=True, states=STATE)
    data_fatura = fields.Datetime(
        string='Data Entrada/Saída', readonly=True, states=STATE)
    ambiente = fields.Selection(
        [('homologacao', 'Homologação'),
         ('producao', 'Produção')],
        string='Ambiente', readonly=True, states=STATE)
    finalidade_emissao = fields.Selection(
        [('1', '1 - Normal'),
         ('2', '2 - Complementar'),
         ('3', '3 - Ajuste'),
         ('4', '4 - Devolução')],
        string='Finalidade', help=u"Finalidade da emissão de NFe",
        readonly=True, states=STATE)
    #invoice_id = fields.Many2one(
    #    'account.move', string='Fatura', readonly=True, states=STATE)
    invoice_id = fields.Integer(
        string='Fatura', readonly=True)
    partner_id = fields.Many2one(
        'res.partner', string='Parceiro', readonly=True, states=STATE)
    commercial_partner_id = fields.Many2one(
        'res.partner', string='Commercial Entity',
        related='partner_id.commercial_partner_id', store=True)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Entrega', readonly=True, states=STATE)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Condição pagamento',
        readonly=True, states=STATE)
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Posição Fiscal',
        readonly=True, states=STATE)
    eletronic_item_ids = fields.One2many(
        'br_odoo.nfe.item', 'invoice_eletronic_id', string=u"Linhas",
        readonly=True, states=STATE)
    # eletronic_event_ids = fields.One2many(
    #     'br_odoo.nfe.event', 'invoice_eletronic_id', string=u"Eventos",
    #     readonly=True, states=STATE)
    valor_bruto = fields.Monetary(
        string='Total Produtos', readonly=True, states=STATE)
    valor_frete = fields.Monetary(
        string='Total Frete', readonly=True, states=STATE)
    valor_seguro = fields.Monetary(
        string='Total Seguro', readonly=True, states=STATE)
    valor_desconto = fields.Monetary(
        string='Total Desconto', readonly=True, states=STATE)
    valor_despesas = fields.Monetary(
        string='Total Despesas', readonly=True, states=STATE)
    valor_bc_icms = fields.Monetary(
        string=u"Base de Cálculo ICMS", readonly=True, states=STATE)
    valor_icms = fields.Monetary(
        string=u"Total do ICMS", readonly=True, states=STATE)
    valor_icms_deson = fields.Monetary(
        string='ICMS Desoneração', readonly=True, states=STATE)
    valor_bc_icmsst = fields.Monetary(
        string='Total Base ST', help=u"Total da base de cálculo do ICMS ST",
        readonly=True, states=STATE)
    valor_icmsst = fields.Monetary(
        string='Total ST', readonly=True, states=STATE)
    valor_ii = fields.Monetary(
        string='Total II', readonly=True, states=STATE)
    valor_ipi = fields.Monetary(
        string=u"Total IPI", readonly=True, states=STATE)
    valor_pis = fields.Monetary(
        string=u"Total PIS", readonly=True, states=STATE)
    valor_cofins = fields.Monetary(
        string=u"Total COFINS", readonly=True, states=STATE)
    valor_estimado_tributos = fields.Monetary(
        string=u"Tributos Estimados", readonly=True, states=STATE)

    valor_servicos = fields.Monetary(
        string=u"Total Serviços", readonly=True, states=STATE)
    valor_bc_issqn = fields.Monetary(
        string=u"Base ISS", readonly=True, states=STATE)
    valor_issqn = fields.Monetary(
        string=u"Total ISS", readonly=True, states=STATE)
    valor_pis_servicos = fields.Monetary(
        string=u"Total PIS Serviços", readonly=True, states=STATE)
    valor_cofins_servicos = fields.Monetary(
        string=u"Total Cofins Serviço", readonly=True, states=STATE)

    valor_retencao_issqn = fields.Monetary(
        string=u"Retenção ISSQN", readonly=True, states=STATE)
    valor_retencao_pis = fields.Monetary(
        string=u"Retenção PIS", readonly=True, states=STATE)
    valor_retencao_cofins = fields.Monetary(
        string=u"Retenção COFINS", readonly=True, states=STATE)
    valor_bc_irrf = fields.Monetary(
        string=u"Base de Cálculo IRRF", readonly=True, states=STATE)
    valor_retencao_irrf = fields.Monetary(
        string=u"Retenção IRRF", readonly=True, states=STATE)
    valor_bc_csll = fields.Monetary(
        string=u"Base de Cálculo CSLL", readonly=True, states=STATE)
    valor_retencao_csll = fields.Monetary(
        string=u"Retenção CSLL", readonly=True, states=STATE)
    valor_bc_inss = fields.Monetary(
        string=u"Base de Cálculo INSS", readonly=True, states=STATE)
    valor_retencao_inss = fields.Monetary(
        string=u"Retenção INSS", help=u"Retenção Previdência Social",
        readonly=True, states=STATE)

    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Company Currency")
    valor_final = fields.Monetary(
        string='Valor Final', readonly=True, states=STATE)

    informacoes_legais = fields.Text(
        string='Informações legais', readonly=True, states=STATE)
    informacoes_complementares = fields.Text(
        string='Informações complementares', readonly=True, states=STATE)

    codigo_retorno = fields.Char(
        string='Código Retorno', readonly=True, states=STATE,
        tracking=True)
    mensagem_retorno = fields.Char(
        string='Mensagem Retorno', readonly=True, states=STATE,
        tracking=True)
    numero_nfe = fields.Char(
        string=u"Numero Formatado NFe", readonly=True, states=STATE)

    xml_to_send = fields.Binary(string="Xml a Enviar", readonly=True)
    xml_to_send_name = fields.Char(
        string=u"Nome xml a ser enviado", size=100, readonly=True)

    email_sent = fields.Boolean(string=u"Email enviado", default=False,
                                readonly=True, states=STATE)
    
    payment_mode_id = fields.Integer(string='Modo de Pagamento')

    # payment_mode_id = fields.Many2one(
    #     'l10n_br.payment.mode', string='Modo de Pagamento',
    #     readonly=True, states=STATE)
    iest = fields.Char(string="IE Subst. Tributário")
    ambiente_nfe = fields.Selection(
        [('producao', 'Produção'), ('homologacao', 'Homologação')],
        string=u"Ambiente NFe",
        readonly=True)
    ind_final = fields.Selection([
        ('0', 'Não'),
        ('1', 'Sim')
    ], 'Consumidor Final', readonly=True, states=STATE, required=False,
        help='Indica operação com Consumidor final.', default='0')
    ind_pres = fields.Selection([
        ('0', 'Não se aplica'),
        ('1', 'Operação presencial'),
        ('2', 'Operação não presencial, pela Internet'),
        ('3', 'Operação não presencial, Teleatendimento'),
        ('4', 'NFC-e em operação com entrega em domicílio'),
        ('5', 'Operação presencial, fora do estabelecimento'),
        ('9', 'Operação não presencial, outros'),
    ], 'Indicador de Presença', readonly=True, states=STATE, required=False,
        help='Indicador de presença do comprador no\n'
             'estabelecimento comercial no momento\n'
             'da operação.', default='0')
    ind_dest = fields.Selection([
        ('1', '1 - Operação Interna'),
        ('2', '2 - Operação Interestadual'),
        ('3', '3 - Operação com exterior')],
        string=u"Indicador Destinatário", readonly=True, states=STATE)
    ind_ie_dest = fields.Selection([
        ('1', '1 - Contribuinte ICMS'),
        ('2', '2 - Contribuinte Isento de Cadastro'),
        ('9', '9 - Não Contribuinte')],
        string=u"Indicador IE Dest.", help=u"Indicador da IE do desinatário",
        readonly=True, states=STATE)
    tipo_emissao = fields.Selection([
        ('1', '1 - Emissão normal'),
        ('2', '2 - Contingência FS-IA, com impressão do DANFE em formulário \
         de segurança'),
        ('3', '3 - Contingência SCAN'),
        ('4', '4 - Contingência DPEC'),
        ('5', '5 - Contingência FS-DA, com impressão do DANFE em \
         formulário de segurança'),
        ('6', '6 - Contingência SVC-AN'),
        ('7', '7 - Contingência SVC-RS'),
        ('9', '9 - Contingência off-line da NFC-e')],
        string=u"Tipo de Emissão", readonly=True, states=STATE, default='1')

    # Transporte
    data_entrada_saida = fields.Datetime(
        string="Data Entrega", help="Data para saída/entrada das mercadorias")
    modalidade_frete = fields.Selection(
        [('0', '0 - Contratação do Frete por conta do Remetente (CIF)'),
         ('1', '1 - Contratação do Frete por conta do Destinatário (FOB)'),
         ('2', '2 - Contratação do Frete por conta de Terceiros'),
         ('3', '3 - Transporte Próprio por conta do Remetente'),
         ('4', '4 - Transporte Próprio por conta do Destinatário'),
         ('9', '9 - Sem Ocorrência de Transporte')],
        string='Modalidade do frete', default="9",
        readonly=True, states=STATE)
    transportadora_id = fields.Many2one(
        'res.partner', string=u"Transportadora", readonly=True, states=STATE)
    placa_veiculo = fields.Char(
        string='Placa do Veículo', size=7, readonly=True, states=STATE)
    uf_veiculo = fields.Char(
        string='UF da Placa', size=2, readonly=True, states=STATE)
    rntc = fields.Char(
        string="RNTC", size=20, readonly=True, states=STATE,
        help=u"Registro Nacional de Transportador de Carga")

    # reboque_ids = fields.One2many(
    #     'nfe.reboque', 'invoice_eletronic_id',
    #     string=u"Reboques", readonly=True, states=STATE)
    # volume_ids = fields.One2many(
    #     'nfe.volume', 'invoice_eletronic_id',
    #     string=u"Volumes", readonly=True, states=STATE)

    # Exportação
    uf_saida_pais_id = fields.Many2one(
        'res.country.state', domain=[('country_id.code', '=', 'BR')],
        string="UF Saída do País", readonly=True, states=STATE)
    local_embarque = fields.Char(
        string='Local de Embarque', size=60, readonly=True, states=STATE)
    local_despacho = fields.Char(
        string='Local de Despacho', size=60, readonly=True, states=STATE)

    # Cobrança
    numero_fatura = fields.Char(
        string=u"Fatura", readonly=True, states=STATE)
    fatura_bruto = fields.Monetary(
        string=u"Valor Original", readonly=True, states=STATE)
    fatura_desconto = fields.Monetary(
        string=u"Desconto", readonly=True, states=STATE)
    fatura_liquido = fields.Monetary(
        string=u"Valor Líquido", readonly=True, states=STATE)

    # duplicata_ids = fields.One2many(
    #     'nfe.duplicata', 'invoice_eletronic_id',
    #     string=u"Duplicatas", readonly=True, states=STATE)

    # Compras
    nota_empenho = fields.Char(
        string="Nota de Empenho", size=22, readonly=True, states=STATE)
    pedido_compra = fields.Char(
        string="Pedido Compra", size=60, readonly=True, states=STATE)
    contrato_compra = fields.Char(
        string="Contrato Compra", size=60, readonly=True, states=STATE)

    sequencial_evento = fields.Integer(
        string=u"Sequêncial Evento", default=1, readonly=True, states=STATE)
    recibo_nfe = fields.Char(
        string=u"Recibo NFe", size=50, readonly=True, states=STATE)
    chave_nfe = fields.Char(
        string=u"Chave NFe", size=50, readonly=True, states=STATE)
    chave_nfe_danfe = fields.Char(
        string=u"Chave Formatado", compute="_compute_format_danfe_key")
    protocolo_nfe = fields.Char(
        string=u"Protocolo", size=50, readonly=True, states=STATE,
        help=u"Protocolo de autorização da NFe")
    nfe_processada = fields.Binary(string=u"Xml da NFe", readonly=True)
    nfe_processada_name = fields.Char(
        string=u"Xml da NFe", size=100, readonly=True)

    valor_icms_uf_remet = fields.Monetary(
        string=u"ICMS Remetente", readonly=True, states=STATE,
        help='Valor total do ICMS Interestadual para a UF do Remetente')
    valor_icms_uf_dest = fields.Monetary(
        string=u"ICMS Destino", readonly=True, states=STATE,
        help='Valor total do ICMS Interestadual para a UF de destino')
    valor_icms_fcp_uf_dest = fields.Monetary(
        string=u"Total ICMS FCP", readonly=True, states=STATE,
        help='Total total do ICMS relativo Fundo de Combate à Pobreza (FCP) \
        da UF de destino')

    # NFC-e
    qrcode_hash = fields.Char(string='QR-Code hash')
    qrcode_url = fields.Char(string='QR-Code URL')
    metodo_pagamento = fields.Selection(
        [('01', 'Dinheiro'),
         ('02', 'Cheque'),
         ('03', 'Cartão de Crédito'),
         ('04', 'Cartão de Débito'),
         ('05', 'Crédito Loja'),
         ('10', 'Vale Alimentação'),
         ('11', 'Vale Refeição'),
         ('12', 'Vale Presente'),
         ('13', 'Vale Combustível'),
         ('15', 'Boleto Bancário'),
         ('90', 'Sem pagamento'),
         ('99', 'Outros')],
        string="Forma de Pagamento", default="01")
    valor_pago = fields.Monetary(string='Valor pago')
    troco = fields.Monetary(string='Troco')

    # # Documentos Relacionados
    # fiscal_document_related_ids = fields.One2many(
    #     'br_account.document.related', 'invoice_eletronic_id',
    #     'Documentos Fiscais Relacionados', readonly=True, states=STATE)

    # CARTA DE CORRECAO
    # cartas_correcao_ids = fields.One2many(
    #     'carta.correcao.eletronica.evento', 'eletronic_doc_id',
    #     string=u"Cartas de Correção", readonly=True, states=STATE)
    
class BrOdooNfeEvent(models.Model):
    _name = 'br_odoo.nfe.event'
    _description = "Eventos de nota fiscal eletrônica"
    _order = 'id desc'

    code = fields.Char(string='Código', readonly=True, states=STATE)
    name = fields.Char(string='Mensagem', readonly=True, states=STATE)
    invoice_eletronic_id = fields.Many2one(
        'br_odoo.nfe', string=u"Fatura Eletrônica",
        readonly=True, states=STATE)
    state = fields.Selection(
        related='invoice_eletronic_id.state', string="State")
