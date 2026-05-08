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
        for res in self.env.company:
            pendings = res.get_pendings_db(config_url, res.name, res.cnpj_cpf_stripped)
            if pendings.status_code == 200:
                if pendings.json()['pendencias']:
                    res.payment_pending = True if pendings.json()['pendencias'][0]['pending'] else False
                    res.mensage_pai = pendings.json()['pendencias'][0]['mensagem']
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
    



   