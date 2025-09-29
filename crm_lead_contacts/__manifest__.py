# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'CRM - Subcontatos do Parceiro',
    'version': '16.0.1.0',
    'category': 'CRM',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Adiciona os Subcontatos do Parceiro no Lead',
    'description': """
        Este Módulo adiciona o campo de Subcontatos no Lead, permitindo que o Cliente traga seus Subcontatos
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ["crm", "base"],
    'data': [
        "views/crm_lead_views.xml",
    ],
    'installable': True,
    'application': False,
}


