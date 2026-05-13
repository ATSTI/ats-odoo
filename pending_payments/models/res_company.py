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
        companies = self if self else self.env.company
        pendings = companies.get_pendings_db(
            config_url,
            companies.name,
            companies.cnpj_cpf_stripped
        )
        if pendings.status_code != 200:
            return True
        response_data = pendings.json()
        pendencias = response_data.get('pendencias', [])
        for data in pendencias:
            pending = data.get('pending', False)
            mensagem = data.get('mensagem', '')
            for company_data in data.get('company_names', []):
                company_name = company_data.get('name')
                if not company_name:
                    continue
                # Busca empresas relacionadas
                found_companies = companies.search([
                    ('name', 'ilike', company_name)
                ])
                if not found_companies:
                    continue
                # Atualiza status
                found_companies.write({
                    'payment_pending': pending,
                    'mensage_pai': mensagem,
                })
        return True    

    def get_pendings_db(self, url, company_name, company_vat):
        base_url = f"{url}/check-pending-payments?company_name={company_name}&company_vat={company_vat}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        response = rq.get(base_url, headers=headers)

        return response
    



   