# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ligação Fiscal - cBenef (benefício fiscal)',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Ligação Fiscal - cBenef (benefício fiscal)',
    'description': """
Ligação Fiscal - cBenef (benefício fiscal)
=======================
Este módulo adiciona ao ICMS o benefício fiscal e faz a busca a partir deles, além disso a instalação do módulo preencha de acordo com a tabela a classifcação respectiva do cBenef
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal',
        'l10n_br_account',
        'l10n_br_nfe',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/cbenef_view.xml',
        'views/ncm_view.xml',
        'views/document_line_view.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}