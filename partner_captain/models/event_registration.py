from odoo import models, fields


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


    nadadeira_id = fields.Many2one(
        'product.product',
        string="Nadadeira",
        ondelete='set null'
    )

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

    def _assign_equipamentos(self):
        Product = self.env['product.product']
        Category = self.env['product.category']

        bcd_category = Category.search([('name', '=', 'BCD')], limit=1)
        suit_category = Category.search([('name', '=', 'SUIT')], limit=1)
        if not bcd_category and not suit_category:
            return
        prioridade_situacao = ['otima', 'bom', 'medio', 'ruim', 'pessimo']
        for reg in self:
            if not reg.event_id or not reg.partner_id:
                continue
            partner = reg.partner_id
            is_owd = reg.event_id.tipo_evento == 'owd'
            equipamentos_proprios = partner.equipamento_ids.filtered(lambda e: not e.is_loan)
            equipamento_bcd = equipamentos_proprios.filtered(lambda e: e.tipo == 'bcd')
            if equipamento_bcd:
                reg.bcd_id = equipamento_bcd[0].product_id
            elif partner.bcd and bcd_category:
                tamanho_bcd = partner.bcd.strip().lower()
                domain_bcd = [
                    ('categ_id', '=', bcd_category.id),
                    ('tamanho_cd', '=', tamanho_bcd),
                    ('usado', '=', False),
                ]
                bcd = False
                if is_owd:
                    for situacao in prioridade_situacao:
                        bcd = Product.search(
                            domain_bcd + [('situacao', '=', situacao)],
                            limit=1
                        )
                        if bcd:
                            break
                else:
                    bcd = Product.search(domain_bcd, limit=1)
                if bcd:
                    reg.bcd_id = bcd
                    bcd.usado = True
            equipamento_suit = equipamentos_proprios.filtered(lambda e: e.tipo == 'suit')
            if equipamento_suit:
                reg.suit_id = equipamento_suit[0].product_id

            elif partner.suit and suit_category:
                tamanho_suit = partner.suit.strip().lower()
                domain_suit = [
                    ('categ_id', '=', suit_category.id),
                    ('tamanho_cd', '=', tamanho_suit),
                    ('usado', '=', False),
                ]
                suit = False
                if is_owd:
                    for situacao in prioridade_situacao:
                        suit = Product.search(
                            domain_suit + [('situacao', '=', situacao)],
                            limit=1
                        )
                        if suit:
                            break
                else:
                    suit = Product.search(domain_suit, limit=1)
                if suit:
                    reg.suit_id = suit
                    suit.usado = True




   