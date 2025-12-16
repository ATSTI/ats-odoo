# -*- coding: utf-8 -*-
# © 2017 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Relatório Safra',
    'version': '1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Relatórios Personalizados",
    'description': """
        Esse Módulo Adiciona relatórios personalizados para o Módulo de Vendas.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['br_sale'],
    'data': [
        'reports/report_saleorder_safra.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}