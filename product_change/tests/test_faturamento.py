# -*- coding: utf-8 -*-
# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class TestFaturamento(TransactionCase):

    def setUp(self):
        super(TestFaturamento, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_2')
        self.product.description_sale = 'Test description sale'
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
            'payment_mode_id': 1, # Santander
            'payment_term_id': 8, # dia 10
            'fiscal_position_id': 4,
            'divisao': 1,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        self.contract_line = self.env['account.analytic.invoice.line'].create({
            'analytic_account_id': self.contract.id,
            'product_id': self.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': self.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        })




        self.cliente_1 = self.env['res.partner'].create({
            'name': 'Cliente 1'
        })
        self.contrato_1 = self.env['account.analytic.account'].create({
            'name': 'Jogador Ranking 3'
        })
        self.jogador_rk4 = self.env['res.partner'].create({
            'name': 'Jogador Ranking 4'
        })
        self.jogador_rk7 = self.env['res.partner'].create({
            'name': 'Jogador Ranking 7'
        })

        self.env['tenis.ranqueamento'].create({
            'jogador_id': self.jogador_rk7.id,
            'rk': 7
        })

        self.env['tenis.ranqueamento'].create({
            'jogador_id': self.jogador_rk1.id,
            'rk': 1
        })

        self.env['tenis.ranqueamento'].create({
            'jogador_id': self.jogador_rk3.id,
            'rk': 3
        })

        self.env['tenis.ranqueamento'].create({
            'jogador_id': self.jogador_rk4.id,
            'rk': 4
        })

        self.falhar1 = self.env['tenis.ranking'].create({
            'desafiante_id': self.jogador_rk4.id,
            'desafiado_id': self.jogador_rk1.id,
            'name':'jogo 2'
        })

    """
    def test_regras_desafiante(self):
        desafio = self.env['tenis.ranking'].create({
            'desafiante_id': self.jogador_rk1.id,
            'desafiado_id': self.jogador_rk4.id,
            'name':'jogo 1'
        })
        self.assertTrue(desafio)
    """
    def test_regras_desafiante_correto1(self):
        tn = self.env['tenis.ranking']
        regras = tn.regras_desafiante(self.jogador_rk4.id, self.jogador_rk1.id)
        self.assertTrue(regras)

    def test_regras_desafiante_correto2(self):
        tn = self.env['tenis.ranking']
        regras = tn.regras_desafiante(self.jogador_rk1.id, self.jogador_rk3.id)
        self.assertTrue(regras)

    def test_regras_desafiante_errado1(self):
        tn = self.env['tenis.ranking']
        regras = tn.regras_desafiante(self.jogador_rk7.id, self.jogador_rk1.id)
        self.assertFalse(regras)

