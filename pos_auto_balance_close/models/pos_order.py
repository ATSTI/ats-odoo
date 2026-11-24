import logging

from odoo import models, _

_logger = logging.getLogger(__name__)

CODIGO_CONTA_DIFERENCA = '1.1.2.03'  
TOLERANCIA_DIFERENCA = 1.0          


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _close_session_action(self, amount_to_balance):
        self.ensure_one()
        if abs(amount_to_balance) <= TOLERANCIA_DIFERENCA:
            account = self.env['account.account'].sudo().search([
                ('code', '=', CODIGO_CONTA_DIFERENCA),
                ('company_id', '=', self.company_id.id),
            ], limit=1)

            if account:
                _logger.info(
                    "Sessão %s: fechando automaticamente com diferença de %s "
                    "na conta %s",
                    self.name, amount_to_balance, account.display_name,
                )
                result = self.action_pos_session_closing_control(
                    balancing_account=account.id,
                    amount_to_balance=amount_to_balance,
                )
                self.message_post(body=_(
                    "Diferença de fechamento de %(valor).2f lançada "
                    "automaticamente na conta %(conta)s.",
                    valor=amount_to_balance, conta=account.display_name,
                ))
                return result

            _logger.warning(
                "Sessão %s: conta %s não encontrada na empresa %s, "
                "abrindo wizard padrão.",
                self.name, CODIGO_CONTA_DIFERENCA, self.company_id.name,
            )

        return super()._close_session_action(amount_to_balance)