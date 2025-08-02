# Copyright (C) 2020 - Carlos R. Silveira - ATSti Soluções
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
 
import os
import base64
from mock import patch
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestSpedEfdContribuicoes(TransactionCase):

    def setUp(self):
        super(TestSpedEfdContribuicoes, self).setUp()
        print('zzzzzzzzzzzz')
        import pudb;pu.db
        self.main_company = self.env.ref('base.main_company')
        self.main_company.write({
            'name': 'Trustcode',
            'legal_name': 'Trustcode Tecnologia da Informação',
            'cnpj_cpf': '92.743.275/0001-33',
            'zip': '88037-240',
            'street': 'Vinicius de Moraes',
            'number': '42',
            'district': 'Córrego Grande',
            'country_id': self.env.ref('base.br').id,
            'state_id': self.env.ref('base.state_br_sc').id,
            'city_id': 3144,
            'phone': '(48) 9801-6226',
        })
        self.main_company.write({'inscr_est': '219.882.606'})
        self.default_ncm = self.env["product.fiscal.classification"].create({
            'code': '0201.20.20',
            'name': 'Furniture',
            'federal_nacional': 10.0,
            'estadual_imposto': 10.0,
            'municipal_imposto': 10.0,
            'cest': '17.084.00'
        })
        self.default_product = self.env['product.product'].create({
            'name': 'Normal Product',
            'default_code': '12',
            'fiscal_classification_id': self.default_ncm.id,
            'list_price': 15.0
        })
        self.product_2 = self.env['product.product'].create({
            'name': 'Product 2',
            'default_code': '13',
            'fiscal_classification_id': self.default_ncm.id,
            'list_price': 25.0
        })
        self.st_product = self.env['product.product'].create({
            'name': 'Product for ICMS ST',
            'default_code': '15',
            'fiscal_classification_id': self.default_ncm.id,
            'list_price': 25.0
        })
        default_partner = {
            'name': 'Nome Parceiro',
            'legal_name': 'Razão Social',
            'zip': '88037-240',
            'street': 'Endereço Rua',
            'number': '42',
            'district': 'Centro',
            'phone': '(48) 9801-6226',
            'property_account_receivable_id': self.receivable_account.id,
        }
        self.partner_juridica = self.env['res.partner'].create(dict(
            default_partner.items(),
            cnpj_cpf='05.075.837/0001-13',
            company_type='company',
            is_company=True,
            country_id=self.env.ref('base.br').id,
            state_id=self.env.ref('base.state_br_sc').id,
            city_id=self.env.ref('br_base.city_4205407').id,
            inscr_est='433.992.727',
        ))
        self.partner_juridica_inter = self.env['res.partner'].create(dict(
            default_partner.items(),
            cnpj_cpf='08.326.476/0001-29',
            company_type='company',
            is_company=True,
            country_id=self.env.ref('base.br').id,
            state_id=self.env.ref('base.state_br_rs').id,
            city_id=self.env.ref('br_base.city_4300406').id,
        ))
        self.partner_juridica_sp = self.env['res.partner'].create(dict(
            default_partner.items(),
            cnpj_cpf='37.484.824/0001-94',
            company_type='company',
            is_company=True,
            country_id=self.env.ref('base.br').id,
            state_id=self.env.ref('base.state_br_sp').id,
            city_id=self.env.ref('br_base.city_3501608').id,
        ))

        self.journalrec = self.env['account.journal'].create({
            'name': 'Faturas',
            'code': 'INV',
            'type': 'sale',
            'default_debit_account_id': self.revenue_account.id,
            'default_credit_account_id': self.revenue_account.id,
        })

        self.fiscal_doc = self.env['br_account.fiscal.document'].create(dict(
            code='55',
            electronic=True
        ))

        self.serie = self.env['br_account.document.serie'].create(dict(
            code='1',
            active=True,
            name='serie teste',
            fiscal_document_id=self.fiscal_doc.id,
            fiscal_type='product',
            company_id=self.main_company.id,
        ))
        self.icms_difal_inter_700 = self.env['account.tax'].create({
            'name': "ICMS Difal Inter",
            'amount_type': 'division',
            'domain': 'icms_inter',
            'amount': 7,
            'price_include': True,
        })
        self.icms_difal_intra_1700 = self.env['account.tax'].create({
            'name': "ICMS Difal Intra",
            'amount_type': 'division',
            'domain': 'icms_intra',
            'amount': 17,
            'price_include': True,
        })

        self.fpos = self.env['account.fiscal.position'].create({
            'name': 'Venda',
            'product_document_id': self.fiscal_doc.id,
            'product_serie_id': self.serie.id
        })

        self.fpos_consumo = self.env['account.fiscal.position'].create({
            'name': 'Venda Consumo',
            'ind_final': '1',
            'product_document_id': self.fiscal_doc.id,
            'product_serie_id': self.serie.id
        })
        #'icms_valor': 
        invoice_line_data = [
            (0, 0,
                {
                    'product_id': self.default_product.id,
                    'uom_id': self.default_product.uom_id.id,
                    'quantidade': 130.0,
                    'informacao_adicional': 'product test 5',
                    'name': 'product test 5',
                    'preco_unitario': 17.00,
                    'cfop': self.env.ref(
                        'br_data_account_product.cfop_5101').code,
                    'tipo_produto': self.default_product.fiscal_type,
                    'icms_cst': '00',
                    'icms_aliquota': 18,
                    'icms_valor': 397.80,
                    'icms_base_calculo': 2210.0,
                    'origem': 0,
                    'ipi_cst': '00',
                    'ipi_base_calculo': 2210.0,
                    'ipi_aliquota': 0.15,
                    'ipi_valor': 331.50,
                    'pis_cst': '01',
                    'cofins_cst': '01',
                    'fiscal_classification_id': self.default_ncm.id,
                    'tem_difal': True,
                    'tax_icms_inter_id': self.icms_difal_inter_700.id,
                    'tax_icms_intra_id': self.icms_difal_intra_1700.id,
                }
             ),
            (0, 0,
                {
                    'product_id': self.product_2.id,
                    'uom_id': self.product_2.uom_id.id,
                    'quantidade': 10.0,
                    'informacao_adicional': 'product test 2',
                    'name': 'product test 2',
                    'tipo_produto': self.default_product.fiscal_type,
                    'price_unit': 87.46,
                    'cfop_id': self.env.ref(
                        'br_data_account_product.cfop_5101').code,
                    'icms_cst': '00',
                    'origem': 0,
                    'icms_aliquota': 0.18,
                    'icms_valor': 157.428,
                    'icms_base_calculo': 874.60,
                    'origem': 0,
                    'ipi_cst': '00',
                    'ipi_base_calculo': 874.60,
                    'ipi_aliquota': 0.15,
                    'ipi_valor': 131.19,
                    'pis_cst': '01',
                    'cofins_cst': '01',
                }
             )
        ]
        duplicata_data = [
            (0, 0,
                {
                    'numero_duplicata': '001',
                    'valor': 350,
                    'data_vencimento': '2020-04-10',
                }
            )
        ]
        default_einvoince = {
            'name': "Teste Validação",
            'model': '55',
            'fiscal_position_id': self.fpos.id,
            'eletronic_itens_ids': invoice_line_data,
            'serie': self.serie.id,
            'serie_documento': self.serie.code,
            'modalidade_frete': 9,
            'data_agendada': '2020-03-01',
            'data_emissao': '2020-03-01 13:00:00',
            'data_fatura': '2020-03-01 13:00:00',
            'metodo_pagamento': 1,
            'duplicata_ids': duplicata_data,
            'code': 123456,
            'company_id': self.main_company.id,
            'state': 'done',
            'tipo_operacao': 'saida',
            'finalidade_emissao': '1',
            'partner_id': self.partner_juridica_sp.id,
            'payment_term_id': 1,
            'fiscal_position_id': self.fpos.id,
            'valor_icms': 555.228,
            'valor_icmsst': 0.0,
            'valor_ipi': 462.69,
            'valor_pis': 0.0,
            'valor_cofins': 0.0,
            'valor_ii': 0.0,
            'valor_bruto': 3084.60,
            'valor_desconto': 0.0,
            'valor_final': 3084.60,
            'valor_bc_icms': 3084.60,
            'valor_bc_icmsst': 0.0,
        }
        self.nfe = self.env['invoice.eletronic'].create(dict(
            name="Teste Validação",
            product_document_id=self.env.ref(
                'br_data_account.fiscal_document_55').id,
            journal_id=self.journalrec.id,
            partner_id=self.partner_fisica.id,
            invoice_line_ids=self.invoice_line_data,
            duplicata_ids=self.duplicata_ids,
            product_serie_id=self.serie.id,
            fiscal_position_id=self.fpos.id,
        ))
        import pudb;pu.db
        periodo = 'date_trunc(\'day\', ie.data_fatura) \
            between \'2020-03-01\' and \'2020-03-31\''
        sped = self.env['sped.efd.contribuicoes']
        self.sped = sped.query_registro0150(periodo)

    def test_basic_validation_for_sped_contribuicoes(self):
        print('xxxxxxx')
        import pudb;pu.db
        self.assertEquals(self.sped, 0)
        """
        vals = self.inv_incomplete.action_view_edocs()
        self.assertEquals(vals['type'], 'ir.actions.act_window')
        self.assertEquals(vals['res_model'], 'invoice.eletronic')
        self.assertEquals(vals['res_id'], 0)
        with self.assertRaises(UserError):
            self.inv_incomplete.action_invoice_open()

        invoice_eletronic = self.env['invoice.eletronic'].search(
            [('invoice_id', '=', self.inv_incomplete.id)])

        self.assertEquals(self.inv_incomplete.total_edocs, 0)
        vals = self.inv_incomplete.action_view_edocs()
        self.assertEquals(vals['type'], 'ir.actions.act_window')
        self.assertEquals(vals['res_model'], 'invoice.eletronic')
        self.assertEquals(vals['res_id'], invoice_eletronic.id)
        """
