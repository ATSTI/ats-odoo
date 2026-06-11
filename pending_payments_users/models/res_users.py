from odoo import models, fields, api
from odoo.tools import config
import unicodedata
import requests as rq
import logging

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    payment_pending = fields.Boolean(string="Pagamento Pendente", default=False)
    mensage_pai = fields.Char(string="Mensagem Pai", default=False)

    # Logo no Login já verifico se existe pendencia
    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        """Override do authenticate para verificar pendências no login."""
        uid = super().authenticate(db, login, password, user_agent_env)
        if uid:
            try:
                with cls.pool.cursor() as cr:
                    env = api.Environment(cr, uid, {})
                    env['res.users'].browse(uid).sudo()._check_pending_payments()
            except Exception as e:
                _logger.warning('[PendingPayment] Erro ao verificar pendência no login: %s', e)
        return uid

    def refresh_pending_payment(self):
        self.ensure_one()
        _logger.info(f'[PendingPayment] Atualizando pendências para usuário {self.login} (ID: {self.id})')
        self._check_pending_payments()
        _logger.info(f'[PendingPayment] Pendências atualizadas: payment_pending={self.payment_pending}, mensage_pai="{self.mensage_pai}"')
        return {
            'payment_pending': self.payment_pending,
            'mensage_pai': self.mensage_pai,
        }

    def _check_pending_payments(self):
        """Verifica pendências de pagamento para a empresa atual do usuário."""

        def normalize(text):
            text = unicodedata.normalize('NFKD', text)
            text = ''.join(c for c in text if not unicodedata.combining(c))
            return ' '.join(text.upper().split())

        config_url = config.get("owner_pending_url")
        if not config_url:
            _logger.warning('[PendingPayment] owner_pending_url não configurado no odoo.conf')
            return True

        # Usa apenas a empresa atual da sessão
        company = self.company_id
        if not company:
            return True

        try:
            response = self.get_pendings_db(
                config_url,
                company.name,
                company.cnpj_cpf_stripped,
            )
        except Exception as e:
            _logger.warning('[PendingPayment] Falha ao chamar API: %s', e)
            return True

        if response.status_code != 200:
            _logger.warning('[PendingPayment] API retornou status %s', response.status_code)
            return True

        response_data = response.json()
        pendencias = response_data.get('pendencias', [])
        
        found_pending = False
        mensagem_pendente = ''

        for data in pendencias:
            pending = data.get('pending', False)
            mensagem = data.get('mensagem', '')
            company_names = [
                normalize(item['name'])
                for item in data.get('company_names', [])
            ]

            company_normalized = normalize(company.name)

            match = any(
                company_normalized in cn or cn in company_normalized
                for cn in company_names
            )

            if match and pending:
                found_pending = True
                mensagem_pendente = mensagem
                break

        # Atualiza o campo independente do resultado
        self.write({
            'payment_pending': found_pending,
            'mensage_pai': mensagem_pendente if found_pending else '',
        })

        return True

    def get_pendings_db(self, url, company_name, company_vat):
        base_url = (
            f"{url}/check-pending-payments"
            f"?company_name={company_name}"
            f"&company_vat={company_vat}"
        )
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        response = rq.get(base_url, headers=headers, timeout=10)
        return response