# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Customização do Serviço de Campo',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'MOdulo de modificações do modulo de Serviço de Campo',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['fieldservice', 'hr', 'base', 'account', 'fieldservice_isp_account', 'l10n_br_fiscal'],
    'data': [
        'views/fsm_order_view.xml',
        'views/res_partner_view.xml',
        'report/report_paper_format.xml',
        'report/report_cliente.xml',
        'report/report_lavanderia.xml',
        'report/report_faturas_total.xml',
    ],
    'installable': True,
    'application': False,
}
