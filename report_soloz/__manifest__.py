# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio de Orçamento (soloz)',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatorios de orçamento para a soloz',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'sale_order_tag', 'mrp', 'report_cabecalho'],
    'data': [
        'report/report_orcamento_soloz.xml',
        'report/report_separacao_total.xml',
        'views/report_relatorios.xml',
    ],
    'installable': True,
    'application': False,
}
