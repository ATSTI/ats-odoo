# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See https://www.gnu.org/licenses/agpl

{
    'name': 'UTM Menu Visible',
    'version': '1.0',
    'category': 'Marketing',
    'license': 'AGPL-3',
    'summary': 'Exibe o menu Link Tracker (UTM) para usuários internos.',
    'description': """
Este módulo ajusta as permissões de visualização do menu **Link Tracker (UTM)** 
no Odoo, permitindo que usuários internos tenham acesso ao menu de rastreamento
de links.

Funcionalidades:
- Torna visível o menu de UTM (Link Tracker) para usuários internos.
- Mantém o comportamento padrão de segurança do Odoo.
- Não altera regras de acesso ou dados, apenas a visibilidade do menu.

Ideal para equipes de marketing e análise que precisam acessar
os links rastreados sem conceder permissões administrativas.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'utm',
    ],
    'data': [
        'views/utm_menu_inherit.xml',
    ],
    'installable': True,
    'application': False,
}