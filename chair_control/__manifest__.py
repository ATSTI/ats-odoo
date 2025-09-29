# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'Controle de Cadeiras - POS',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'summary': 'Controle de cadeiras em eventos',
    'description': """
        Esse módulo permite organizar a venda de cadeiras para determinados eventos, utilizando do ponto de venda;
        permite também uma tela personalizada para a escolha da cadeira, disponibiliza também a opção de curso para o cliente
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': '',
    'depends': ['base','event_sale', 'event_crm', 'point_of_sale' ],
    'data': [
        'views/chair_view.xml',
        'views/event_view.xml',
        'views/res_partner_view.xml',
        'report/chair_template.xml',
        'report/event_template.xml',
        'security/ir.model.access.csv'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}