from unittest.mock import patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.point_of_sale.models.pos_session import PosSession as BasePosSession


@tagged('post_install', '-at_install')
class TestAutoBalanceClose(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        cls.account = cls.env['account.account'].search([
            ('code', '=', '1.1.2.03'),
            ('company_id', '=', cls.company.id),
        ], limit=1)
        if not cls.account:
            cls.account = cls.env['account.account'].create({
                'code': '1.1.2.03',
                'name': 'Controle de Débitos (POS)',
                'account_type': 'asset_current',
                'company_id': cls.company.id,
            })

        cls.config = cls.env['pos.config'].create({
            'name': 'PDV Teste Auto Balance',
            'company_id': cls.company.id,
        })
        cls.session = cls.env['pos.session'].create({
            'config_id': cls.config.id,
            'user_id': cls.env.uid,
        })

    def test_diferenca_pequena_fecha_automaticamente(self):
        """Diferença dentro da tolerância: usa a conta 1.1.2.03 e não abre wizard."""
        with patch.object(
            type(self.session), 'action_pos_session_closing_control',
            return_value={'successful': True},
        ) as mock_close:
            result = self.session._close_session_action(0.03)

        mock_close.assert_called_once_with(
            balancing_account=self.account.id,
            amount_to_balance=0.03,
        )
        self.assertEqual(result, {'successful': True})
        self.assertIn(
            'lançada automaticamente',
            ' '.join(self.session.message_ids.mapped('body')),
        )

    def test_diferenca_negativa_tambem_fecha(self):
        with patch.object(
            type(self.session), 'action_pos_session_closing_control',
            return_value={'successful': True},
        ) as mock_close:
            self.session._close_session_action(-0.05)

        mock_close.assert_called_once_with(
            balancing_account=self.account.id,
            amount_to_balance=-0.05,
        )

    def test_diferenca_acima_da_tolerancia_abre_wizard(self):
        """Acima de R$ 1,00: cai no comportamento padrão (wizard)."""
        with patch.object(
            type(self.session), 'action_pos_session_closing_control',
        ) as mock_close, patch.object(
            BasePosSession, '_close_session_action',
            return_value={'wizard': True},
        ) as mock_super:
            result = self.session._close_session_action(5.00)

        mock_close.assert_not_called()
        mock_super.assert_called_once()
        self.assertEqual(result, {'wizard': True})

    def test_conta_inexistente_abre_wizard(self):
        """Sem a conta 1.1.2.03 na empresa: cai no wizard padrão."""
        self.account.code = '9.9.9.99'
        with patch.object(
            type(self.session), 'action_pos_session_closing_control',
        ) as mock_close, patch.object(
            BasePosSession, '_close_session_action',
            return_value={'wizard': True},
        ):
            result = self.session._close_session_action(0.03)

        mock_close.assert_not_called()
        self.assertEqual(result, {'wizard': True})