# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.ht

{
    'name': 'Customizações Soloz',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Módulo de Customizações Específicas para a Soloz em stock.picking',
    'description': """
        Este módulo tem como finalidade algumas mecanicas que a Empresa pediu, entre elas estão:
        - Lógica nova em stock.picking
        - Relátorios com campos ocultos para determinados usuários/estágios do picking
        - Estados separação/conferencia
        - Conferencia as cegas, ocultando tabelas de DEMANDA e RESERVADO
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Otávio Andretta <otavio12257@gmail.com>',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['crm_claim','base', 'sale_management','mrp','crm','stock','report_soloz'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/crm_claim_form_view.xml',
        'views/stock_picking_view.xml',
        # 'views/wizard_validar_conferencia.xml',
        # 'report/report_operacao_separacao_total_custom.xml',
        # 'report/report_picking_inherit.xml',
        # 'report/report_delivery_document_inherit.xml',
        # 'report/report_separacao_cega_gerente.xml',
    ],


    'installable': True,
    'application': False,
}
