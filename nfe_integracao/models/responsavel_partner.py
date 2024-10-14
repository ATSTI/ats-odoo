# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import csv
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    financeiro = fields.Many2one("res.partner", string="Responsavel FInanceiro")

    def action_corrige_financeiro(self):
        reader = csv.reader(open('/home/publico/tmp/nfe_integracao/dump.csv', 'r'))
        total = 0
        msg = ''
        for row in reader:
            k, v = row
            if k == 'id':
                continue
            print (f"k : {k} , v : {v}")
            prt_id = self.env["res.partner"].browse([int(k)])
            if prt_id:
                total += 1
                msg += prt_id.name + '-' + str(k) + '-' + str(v)
                prt_id.write({'financeiro': v})
        msg = 'total = ' + str(total)
        print(msg)