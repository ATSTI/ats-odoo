# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'CRM - Visitação Escolar',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'CRM - Visita escolar informações',
    'description': """
Visita Escolar - Informações
============================
Este módulo adiciona campos e funcionalidades relacionadas a visitas escolares
dentro do módulo CRM. Ele permite o registro de informações específicas sobre
quem visitou, ano, antiga escola, período pretendido...
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'OtavioAndretta, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_leads.xml',
    ],
    'installable': True,
    'application': False,
}
