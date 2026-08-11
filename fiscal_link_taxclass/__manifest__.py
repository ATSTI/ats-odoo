# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ligação Fiscal - NCM, CFOP e Classificação de Tributos',
    'version': '14.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Ligação Fiscal - NCM, CFOP e Classificação de Tributos',
    'description': """
Ligação Fiscal - NCM, CFOP e Classificação de Tributos
=======================
Este módulo adiciona ao ncm e ao cfop o taxclassification e faz a busca a partir deles, além disso a instalação do módulo preencha de acordo com a tabela a classifcação respectiva do ncm/cfop
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal',
    ],
    'data': [
        # 'data/l10n_br_fiscal.ncm.csv',
        #'views/ncm.xml',
        #'views/cfop.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}