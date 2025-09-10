# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatórios MM Portas',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'ATSti Sistemas',
    'description': """
            Relatórios personalizados para MM Portas
    """,
    'author': 'ATSTi,Odoo Community Association (OCA)',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'l10n_br_sale',
    ],
    'data': [
        'report/report_contrato_mmportas.xml',
        'report/report_actions.xml',
    ],
    'installable': True,
    'application': False,
}
