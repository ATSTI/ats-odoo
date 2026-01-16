from odoo import models, fields, api
from datetime import timedelta


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    product_bcd_id = fields.Many2one(
        'product.template',
        string="BCD atribuído"
    )
    product_suit_id = fields.Many2one(
        'product.template',
        string="Suit atribuído"
    )
    genero = fields.Selection(
        related='partner_id.genero',
        string="Gênero",
        store=True,
        readonly=True
    )
    peso = fields.Integer(
        related='partner_id.peso',
        string="Peso (kg)",
        store=True,
        readonly=True
    )
    altura = fields.Float(
        related='partner_id.altura',
        string="Altura (cm)",
        store=True,
        readonly=True
    )
    calcado = fields.Integer(
        related='partner_id.calcado',
        string="Calçado",
        store=True,
        readonly=True
    )
    nadadeira = fields.Text(string='Nadadeira', related ='partner_id.nadadeira')
    bcd_id = fields.Many2one(
        'product.product',
        string="BCD",
        ondelete='set null'
    )
    suit_id = fields.Many2one(
        'product.product',
        string="Suit",
        ondelete='set null'
    )
    bag_id = fields.Many2one(
        'product.product',
        string="BAG",
        ondelete='set null'
    )
    reg_id = fields.Many2one(
        'product.product',
        string="REG",
        ondelete='set null'
    )
    tipo_evento = fields.Selection(
        [
            ('owd', 'OWD'),
            ('profundo', 'PROFUNDO'),
            ('turismo', 'TURISMO'),
            ('especialidades', 'ESPECIALIDADES'),
            ('outro', 'Outro'),
        ],
        string="Tipo de Evento",
        required=True
    )

    bcd_info = fields.Char(string="BCD proprio")
    suit_info = fields.Char(string="Suit proprio")
    reg_info = fields.Char(string="REG proprio")
    bag_info = fields.Char(string="BAG proprio")


    aviso_equipamento = fields.Text(
        string='Aviso Equipamento',
        compute='_compute_aviso_equipamento',
        store=False
    )

    def _compute_aviso_equipamento(self):
        limite_dias = 7
        agora = fields.Datetime.now()
        Movimento = self.env['partner.equipamento.movimento']
        for reg in self:
            aviso = False
            if not reg.partner_id:
                reg.aviso_equipamento = False
                continue
            entradas = Movimento.search([
                ('partner_id', '=', reg.partner_id.id),
                ('movimento', '=', 'entrada'),
            ])
            mensagens = []
            for ent in entradas:
                saida = Movimento.search([
                    ('equipamento_id', '=', ent.equipamento_id.id),
                    ('movimento', '=', 'saida'),
                    ('data_movimento', '>', ent.data_movimento),
                ], limit=1)
                if not saida:
                    dias = (agora - ent.data_movimento).days
                    if dias >= limite_dias:
                        mensagens.append(
                            f"{ent.equipamento_id.display_name} ({dias} dias na Captain)"
                        )
            if mensagens:
                aviso = "⚠ EQUIPAMENTO NÃO RETIRADO: " + " | ".join(mensagens)
            reg.aviso_equipamento = aviso


    @api.onchange('partner_id')
    def _onchange_aviso_equipamento_captain(self):
        if not self.partner_id:
            return

        limite_dias = 7
        agora = fields.Datetime.now()
        avisos = []

        movimentos = self.env['partner.equipamento.movimento'].search([
            ('partner_id', '=', self.partner_id.id),
            ('movimento', '=', 'entrada'),
        ])

        for mov in movimentos:
            saida = self.env['partner.equipamento.movimento'].search([
                ('equipamento_id', '=', mov.equipamento_id.id),
                ('movimento', '=', 'saida'),
                ('data_movimento', '>', mov.data_movimento),
            ], limit=1)

            if not saida:
                dias = (agora - mov.data_movimento).days
                if dias >= limite_dias:
                    avisos.append(
                        f"{mov.equipamento_id.display_name} — {dias} dias na Captain. Cliente ainda não retirou o equipamento"
                    )

        if avisos:
            return {
                'warning': {
                    'title': 'Equipamento não retirado',
                    'message': '\n'.join(avisos)
                }
            }



    def _assign_equipamentos(self):
        Product = self.env['product.product']
        Category = self.env['product.category']

        bcd_category = Category.search([('name', '=', 'BCD')], limit=1)
        suit_category = Category.search([('name', '=', 'SUIT')], limit=1)
        reg_category = Category.search([('name', '=', 'Reguladores')], limit=1)
        bag_category = Category.search([('name', '=', 'BAG')], limit=1)

        prioridade_situacao = ['otima', 'bom', 'medio', 'ruim', 'pessimo']

        regs_owd = self.filtered(lambda r: r.tipo_evento == 'owd')
        regs_outros = self.filtered(lambda r: r.tipo_evento != 'owd')

        for reg in regs_owd + regs_outros:
            if not reg.event_id or not reg.partner_id:
                continue

            partner = reg.partner_id
            equipamentos_proprios = partner.equipamento_ids
            if equipamentos_proprios.filtered(lambda e: e.tipo == 'bcd'):
                reg.bcd_info = 'Equipamento próprio'
            elif partner.bcd and bcd_category:
                tamanho = partner.bcd.strip().lower()
                domain = [
                    ('categ_id', '=', bcd_category.id),
                    ('tamanho_cd', '=', tamanho),
                    ('usado', '=', False),
                ]
                bcd = False
                for situacao in prioridade_situacao:
                    bcd = Product.search(domain + [('situacao', '=', situacao)], limit=1)
                    if bcd:
                        break
                if bcd:
                    reg.bcd_id = bcd
                    bcd.usado = True
                    reg.bcd_info = False
            if equipamentos_proprios.filtered(lambda e: e.tipo == 'suit'):
                reg.suit_info = 'Equipamento próprio'
            elif partner.suit and suit_category:
                tamanho = partner.suit.strip().lower()
                domain = [
                    ('categ_id', '=', suit_category.id),
                    ('tamanho_cd', '=', tamanho),
                    ('usado', '=', False),
                ]
                suit = False
                for situacao in prioridade_situacao:
                    suit = Product.search(domain + [('situacao', '=', situacao)], limit=1)
                    if suit:
                        break
                if suit:
                    reg.suit_id = suit
                    suit.usado = True
                    reg.suit_info = False
            if equipamentos_proprios.filtered(lambda e: e.tipo == 'reg'):
                reg.reg_info = 'Equipamento próprio'
            elif reg_category:
                domain = [
                    ('categ_id', '=', reg_category.id),
                    ('usado', '=', False),
                ]
                if reg.tipo_evento == 'owd':
                    domain.append(('product_tmpl_id.tipo_reg', '=', 'console_duplo'))
                else:
                    domain.append(('product_tmpl_id.tipo_reg', '=', 'balanceado'))
                regulador = False
                for situacao in prioridade_situacao:
                    regulador = Product.search(domain + [('situacao', '=', situacao)], limit=1)
                    if regulador:
                        break
                if regulador:
                    reg.reg_id = regulador
                    regulador.usado = True
                    reg.reg_info = False
            if equipamentos_proprios.filtered(lambda e: e.tipo == 'bag'):
                reg.bag_info = 'Equipamento próprio'
            elif bag_category:
                domain = [
                    ('categ_id', '=', bag_category.id),
                    ('usado', '=', False),
                ]
                bag = False
                for situacao in prioridade_situacao:
                    bag = Product.search(domain + [('situacao', '=', situacao)], limit=1)
                    if bag:
                        break
                if bag:
                    reg.bag_id = bag
                    bag.usado = True
                    reg.bag_info = False


    def action_limpar_equipamento(self):
        PartnerEquip = self.env['partner.equipamento']
        for reg in self:
            partner = reg.partner_id
            if reg.bcd_id:
                equipamento_proprio = PartnerEquip.search([
                    ('partner_id', '=', partner.id),
                    ('tipo', '=', 'bcd'),
                ], limit=1)

                if not equipamento_proprio:
                    reg.bcd_id.usado = False
                reg.bcd_id = False
            if reg.suit_id:
                equipamento_proprio = PartnerEquip.search([
                    ('partner_id', '=', partner.id),
                    ('tipo', '=', 'suit'),
                ], limit=1)

                if not equipamento_proprio:
                    reg.suit_id.usado = False
                reg.suit_id = False
            if reg.reg_id:
                equipamento_proprio = PartnerEquip.search([
                    ('partner_id', '=', partner.id),
                    ('tipo', '=', 'reg'),
                ], limit=1)

                if not equipamento_proprio:
                    reg.reg_id.usado = False
                reg.reg_id = False
            if reg.bag_id:
                equipamento_proprio = PartnerEquip.search([
                    ('partner_id', '=', partner.id),
                    ('tipo', '=', 'bag'),
                ], limit=1)

                if not equipamento_proprio:
                    reg.bag_id.usado = False
                reg.bag_id = False
        return True







   