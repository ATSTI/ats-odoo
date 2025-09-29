
from odoo import models, _, api, fields
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"
    _inherits = {"l10n_br_fiscal.document": "fiscal_document_id"}
    
    card_ids = fields.One2many(
        "card.info.payment",
        "am_id",
        string='Transportadora',
        copy=False,
    )

    fiscal_payment_mode = fields.Selection(
        related="payment_mode_id.fiscal_payment_mode",
        store=True,
        invisible=True,
    )


class CardInfoPayment(models.Model):
    _name = "card.info.payment"
    _description = "Informações do Cartão"

    # payment_method = fields.Char(string="Método de Pagamento")
    # payment_processor_register = fields.Char(string="CNPJ do banco")
    # card_brand = fields.Char(string="Bandeira do Cartão")
    # transaction_id = fields.Char(string="ID da Transação")

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

    am_id = fields.Many2one(
        comodel_name="account.move", 
        string="Documento"
    )

    @api.onchange("nfe40_CNPJ")
    def _onchange_nfe40_CNPJ(self):
        if self.nfe40_CNPJ:
            cnpj = self.nfe40_CNPJ
            if len(cnpj) == 14:
                cnpj = cnpj.zfill(14)
                cnpj = '{}.{}.{}/{}-{}'.format(cnpj[:2], cnpj[2:5], cnpj[5:8], cnpj[8:12], cnpj[12:])
            self.nfe40_CNPJ = cnpj