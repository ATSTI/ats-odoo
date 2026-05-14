from odoo import models, fields, api
from odoo.tools import config
from odoo.exceptions import UserError
import requests as rq

class Company(models.Model):
    _inherit = 'res.company'

    payment_pending = fields.Boolean(string="Pagamento Pendente", default=False)
    mensage_pai = fields.Char(string="Mensagem Pai", default=False)

    def _check_pending_payments(self):
        config_url = config.get("owner_pending_url")
        res = self.env.company if not self else self
        pendings = res.get_pendings_db(config_url, res.name, res.cnpj_cpf_stripped)
        if pendings.status_code == 200:
            for data in pendings.json()['pendencias']:
                for company in data['company_names']:
                    cmp = res.search(['|', ('name', 'ilike', company['name']), ('id', '=', res.id)])
                    for cmp in cmp:
                        cmp.payment_pending = True if data['pending'] else False
                        cmp.mensage_pai = data['mensagem']
                return True
            else:
                res.payment_pending = False
                res.mensage_pai = ""
        return True    

    def get_pendings_db(self, url, company_name, company_vat):
        base_url = f"{url}/check-pending-payments?company_name={company_name}&company_vat={company_vat}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = rq.get(base_url, headers=headers)

        return response
    



   