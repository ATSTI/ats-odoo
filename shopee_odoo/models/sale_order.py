
from odoo import models, _, api, fields
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    nfe40_CNPJ = fields.Char(
        string="CNPJ da instituição de pagamento", xsd_type="TCnpj"
    )

    nfe40_tBand = fields.Selection([
        ('01', 'Visa'),
        ('02', 'Mastercard'),
        ('03', 'American Express'),
        ('04', 'Sorocred'),
        ('05', 'Diners Club'),
        ('06', 'Elo'),
        ('07', 'Hipercard'),
        ('08', 'Aura'),
        ('09', 'Cabal'),
        ('10', 'Alelo'),
        ('11', 'Banes Card'),
        ('12', 'CalCard'),
        ('13', 'Credz'),
        ('14', 'Discover'),
        ('15', 'GoodCard'),
        ('16', 'GreenCard'),
        ('17', 'Hiper'),
        ('18', 'JCB'),
        ('19', 'Mais'),
        ('20', 'MaxVan'),
        ('21', 'Policard'),
        ('22', 'RedeCompras'),
        ('23', 'Sodexo'),
        ('24', 'ValeCard'),
        ('25', 'Verocheque'),
        ('26', 'VR'),
        ('27', 'Ticket'),
        ('99', 'Outros'),
    ], string="Bandeira do Cartão")

    nfe40_cAut = fields.Char(
        string="Número de autorização da operação",
        help=(
            "Número de autorização da operação com cartões, PIX, boletos e "
            "outros pagamentos eletrônicos"
        ),
    )

    @api.onchange("nfe40_CNPJ")
    def _onchange_nfe40_CNPJ(self):
        if self.nfe40_CNPJ:
            cnpj = self.nfe40_CNPJ
            if len(cnpj) == 14:
                cnpj = cnpj.zfill(14)
                cnpj = '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])
            self.nfe40_CNPJ = cnpj

    def _prepare_invoice(self):
        result = super()._prepare_invoice()
        if self.user_id.id == 58:
            result.update({'journal_id': 22})
        if self.user_id.id == 59:
            result.update({'journal_id': 23})            
        result.update({
            "card_ids": [
                (0, 0, {
                    "nfe40_CNPJ": self.nfe40_CNPJ,
                    "nfe40_tBand": self.nfe40_tBand,
                    "nfe40_cAut": self.nfe40_cAut,
                })
            ]
        })
        return result