# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Customizações Soloz',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de Customizações Específicas para a Soloz',
    'description': """
        Este módulo tem como finalidade algumas mecanicas que a Empresa pediu, entre elas estão:
        - Limitação do responsavel pelo cliente
        - Validação das informações do cliente
        - LogCheatter de alterações no Produto
        - Estados separação/conferencia
        - Conferencia as cegas, ocultando tabelas de DEMANDA e RESERVADO
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi, Otávio Andretta',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['base', 'sale_management','stock','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/crm_claim_form_view.xml',
        'views/stock_picking_view.xml',
    ],


    'installable': True,
    'application': False,
}
