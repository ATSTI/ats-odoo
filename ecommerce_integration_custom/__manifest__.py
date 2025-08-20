# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': "Complementos de integração com E-Commerce's",
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Esse Modulo é um complementar para os modulos Shopee e Meli e suas respectivas Integrações. + Um relatório personalizado d elista de separação',
    'description': """
    """,
    'author': 'ATSTi',
    'maintainer': 'Mauricio Silveira, mauricio@atsti.com.br',
    'website': '',
    'depends': ['account', 'sale', 'shopee_odoo', 'meli_odoo', 'auditlog'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_separacao_felicita.xml',
        'views/sale_view.xml',
        'views/report_orcamento.xml',
        'wizard/importar_view.xml',
    ],
    'installable': True,
    'application': False,
}
