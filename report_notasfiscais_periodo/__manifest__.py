# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatório para facilitar a consulta de Notas Fiscais por período',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSTi Soluções',
    'description': """
            Relatório para facilitar a consulta de Notas Fiscais por período, usando um wizard que filtra por data (inicial e final) e gera um qweb pronto e fácil de se usar
    """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'maintainer': 'OtavioAndretta <otavio12257@gmail.com>',
    'website': '',
    'depends': [
        'l10n_br_sale','base','sale','account','product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/notas_fiscais_wizard_view.xml',
        'report/report_notasperiodo_document.xml',
    ],
    'installable': True,
    'application': False,
}