# -*- encoding: utf-8 -*-

{
    'name': 'Partner Captain',
    'description': """
Lista de Equipamentos, Viagens e Cursos do Cliente:
    Armazena no cadastro do cliente, todos os itens que este comprar,
    ou declarar que possui;
    No cadastro do produto foi criado o campo 
       Tipo Produto : Equipamento, Curso, Viagem;
    Estes itens podem ser inseridos direto no cadastro do cliente ou
    serao inseridos pelo pedido de venda, quando o pedido de venda
    for Confirmado com itens do Tipo acima.
    """,
    'version': '1.0',
    'category': 'Localisation',
    'author': 'ATSTi Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'l10n_br_base',
        'product',
        'sale',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/captain_size_rule_view.xml',
        'views/product_view.xml',
        'report/report_action.xml',
        'report/report_event_equipamento.xml',
        'views/partner_equipamento_views.xml',
        'views/event_registration.xml',
        'views/event_view.xml',
        'views/crm_historico.xml',
        'wizard/crm_pipeline_create_view.xml',
    ],
    'demo': [],
    'installable': True,
}
