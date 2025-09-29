# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Sale Order - Confirmação com Data',
    'version': '16.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Garante que pedidos de venda confirmados tenham sempre uma data de pedido',
    'description': """
        Este módulo estende o comportamento padrão dos pedidos de venda no Odoo:

        - Na confirmação de um pedido (`sale.order`), garante que o campo *Data do Pedido* (`date_order`)
          esteja sempre definido.
        - Se já existir uma data no pedido, apenas confirma.
        - Se não houver, define automaticamente a data/hora atual.
        - Mantém a lógica original do Odoo para evitar perda de funcionalidades.

        Útil para empresas que precisam assegurar consistência na informação de data dos pedidos
        de venda, evitando confirmações sem registro temporal.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'sale_management',
    ],
    'data': [
        'views/sale_order.xml'
    ],
    'installable': True,
    'application': False,
}
