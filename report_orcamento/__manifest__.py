# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorios Orcamento',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios personalizados',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'sale_order_tag', 'mrp', 'report_cabecalho', 'product'],
    'data': [
        'views/sale_order_view.xml',
        'views/product_view.xml',
        'report/report_cotacao_locefaca.xml',
        'report/report_entregadevolucao_locefaca.xml',
        'report/report_servico_locefaca.xml',
        'report/report_locacao_locefaca.xml',
        'report/report_venda_locefaca.xml',
        'report/report_instalacao_locefaca.xml',
        'report/report_venda_locefaca.xml',
        'views/report_orcamento.xml',
    ],
    'installable': True,
    'application': False,
}
