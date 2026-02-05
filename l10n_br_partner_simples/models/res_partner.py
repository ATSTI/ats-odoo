# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import re
from odoo import models, _, api, fields
from odoo.exceptions import UserError

from odoo.addons.l10n_br_fiscal.constants.fiscal import (
    MODELO_FISCAL_NFE,
 )


class ResPartner(models.Model):
    _inherit = "res.partner"
      
    def corrigir_cidade_partner(self):
        City = self.env['res.city']
        Partner = self.env['res.partner']
        partners = Partner.search([('city', '!=', ""), ('city_id', '=', False)])
        for prt in partners:
            if prt.city == "MOGI GUACU" or prt.city == "MOGI-GUACU":
                prt.city = "Mogi Guaçu"
            if prt.city == "MOGI-MIRIM":
                prt.city = "Mogi Mirim"
            if "SANTO" in prt.city.split() and "POSSE" in prt.city.split():
                prt.city = "Santo Antônio de Posse"
            if prt.city == "JAGUARIUNA":
                prt.city = "Jaguariúna"
            if prt.city == "SAO PAULO":
                prt.city = "São Paulo"
            city_id = City.search([('name', 'ilike', prt.city)])
            if city_id and len(city_id) == 1:
                prt.city_id = city_id
                prt.city = city_id.name
