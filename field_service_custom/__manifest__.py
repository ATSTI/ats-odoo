# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Customização do Serviço de Campo',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de modificações do modulo de Serviço de Campo',
    'description': """
        Este Módulo inclui algumas customizações no Módulo FIELDSERVICE original:
        - Automatização do responsável pelas faturas
        - Marcação de horas
        - Mudanças visuais 
        - +
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio Silveira, ATSTi',
    'website': '',
    'depends': ['fieldservice', 'hr', 'base', 'account', 'l10n_br_fiscal', 'fieldservice_isp_account'],
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
