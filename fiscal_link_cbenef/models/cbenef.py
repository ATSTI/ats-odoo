# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, fields

class Cbenef(models.Model):
    _name = "l10n_br_fiscal.icms.cbenef"

    code = fields.Char(string="Código do Benefício Fiscal", required=True)
    description = fields.Char(string="Descrição do Benefício Fiscal")
    cst = fields.Selection([
        ('00', '00 - Tributada'),
        ('02', '02 - Tributação monofásica própria sobre combustíveis'),
        ('10', '10 - Tributada com permissão de crédito'),
        ('15', '15 - Tributação monofásica'),
        ('20', '20 - Com redução da base de cálculo'),
        ('30', '30 - Isenta ou não tributada e com permissão de crédito'),
        ('40', '40 - Isenta ou não tributada e sem permissão de crédito'),
        ('41', '41 - Isento ou não tr'),
        ('50', '50 - Suspensão'),
        ('51', '51 - Diferimento'),
        ('53', '53 - Difer.'),
        ('60', '60 - Cobrança de ICMS por substituição tributária'),
        ('61', '61 - Tributação monofásica sobre combustíveis cobrada anteriormente'),
        ('70', '70 - Com redução da base de cálculo e com permissão de crédito'),
        ('90', '90 - Outras')
    ], string="CSTs de ICMS")
    name = fields.Char(compute="_compute_name", store=True)

    @api.depends("code", "description")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s - %s/%s" % (rec.code, rec.description, rec.cst)
