# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Relatorio Contas a Receber/Pagar',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Contas a Pagar/Receber Relatorio',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account'],
    'data': [
        'report/contas_pagar_report_templates.xml',
        'report/contas_pagar_report.xml',
        'report/contas_receber_report_templates.xml',
        'report/contas_receber_report.xml',
    ],
    'installable': True,
    'application': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
