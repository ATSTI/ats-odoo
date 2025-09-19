# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Restrição de Local de Estoque',
    'version': '1.0',
    'category': 'Inventory/Stock',
    'license': 'AGPL-3',
    'sequence': 3,
    'summary': 'Restringe a visualização de estoque para um único local configurado',
    'description': """
        Este módulo permite restringir o domínio de estoque para um local específico,
        de acordo com o parâmetro de sistema:
        
        - Parâmetro: **stock.available_location**
        - Valor: ID do local de estoque a ser utilizado.
        
        Quando configurado, o sistema ignora demais locais e considera apenas o definido.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['product','stock'],
    'data': [
        # 'views/product_view.xml'
    ],
    'installable': True,
    'application': False,
}
