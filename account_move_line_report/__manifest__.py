# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio Contas a Receber/Pagar',
    'version': '16.0.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Impressaccountão Relatórios Contas Receber/Pagar',
    'description': """
        Impressão de Relátorios:
        - Contas a Pagar
        - Contas Pagas
        - Contas a Receber
        - Contas Recebida
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['l10n_br_account'],
    'data': [
        'report/contas_pagar_report_templates.xml',
        'report/contas_pagar_report.xml',
        'report/contas_receber_report_templates.xml',
        'report/contas_receber_report.xml',
    ],
    'installable': True,
    'application': False,
}