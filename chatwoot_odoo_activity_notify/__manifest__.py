# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Odoo - Chatwoot / Notificação de Atividades',
    'version': '18.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Envio Mensagem de Vencimento via Chatwoot',
    'description': """
Integração Odoo com Chatwoot
Este módulo adiciona campos e funcionalidades relacionadas ao vencimento de atividades dentro do odoo
e notificando o responsável via Chatwoot
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'mail',
        'chatwoot_odoo'
    ],
    'data': [
        'views/chatwoot_view.xml',
    ],
    'installable': True,
    'application': False,
}
