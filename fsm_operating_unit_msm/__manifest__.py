# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Customizando o campo operating_unit para a MSM',
    'version': '14.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Customizando o campo operating_unit para a MSM',
    'description': """
Customizando o campo operating_unit para a MSM
=======================
Este módulo customiza o campo operating_unit para atender às necessidades específicas da MSM, permitindo uma melhor organização e gestão das unidades operacionais dentro da empresa. Com essa customização, a MSM poderá categorizar suas operações de forma mais eficiente, facilitando a análise e o controle das atividades realizadas em cada unidade operacional.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta <otavio12257@gmail.com>, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'base','account','sale','operating_unit'
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
}