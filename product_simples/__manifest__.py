# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Cadastro de produto simplificado',
    'version': '16.0',
    'category': 'Product',
    'license': 'AGPL-3',
    'summary': 'simplificação do cadastro de produtos',
    'description': """
            Esse Módulo tem finalidade de simplificar a tela de cadastro de produtos.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': [
        'l10n_br_fiscal', 'product', 'product_sequence'
    ],
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': False,
}
