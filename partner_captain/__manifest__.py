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
    Evento: Nova logica adicionada, atribuição de equipamentos para participantes do evento
    seguindo regra de negócio (OWD, situação, equipamentos próprios), relatorios, tabela visual HTML interativa, entre diversas funcionalidades.
    """,
    'version': '1.0',
    'category': 'Localisation',
    'author': 'ATSTi Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
        'Otávio Andretta<otavio12257@gmail.com>',
    ],
    'depends': [
        'l10n_br_base',
        'product',
        'sale',
        'account',
        'event'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'views/account_move_view.xml',
        'views/captain_size_rule_view.xml',
        'views/product_view.xml',
        'report/report_action.xml',
        'report/report_event_equipamento_externo.xml',
        'report/report_event_equipamento_interno.xml',
        'views/partner_equipamento_views.xml',
        'report/captain_size_rule_html.xml',
        'views/event_registration.xml',
        'views/event_view.xml',
        'views/crm_historico.xml',
        'wizard/crm_pipeline_create_view.xml',
    ],
    'demo': [],
    'installable': True,
}
