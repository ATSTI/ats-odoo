# Copyright 2025 ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Captain',
    'version': '16.0.1.0',
    'category': 'Partner',
    'license': 'AGPL-3',
    'summary': 'Gestão de equipamentos, viagens e cursos adquiridos pelos clientes',
    'description': """
Partner Captain
===============

Este módulo armazena, no cadastro do cliente, os itens que ele possui ou comprou.

Funcionalidades:
----------------
- No cadastro do produto foi criado o campo **Tipo Produto**: Equipamento, Curso, Viagem;
- Esses itens podem ser inseridos diretamente no cadastro do cliente;
- Itens também podem ser inseridos automaticamente pelo pedido de venda, quando o pedido é confirmado.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_base','product','sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/product_view.xml',
        'views/crm_historico.xml',
        'wizard/crm_pipeline_create_view.xml',
    ],
    'installable': True,
    'application': False,
}