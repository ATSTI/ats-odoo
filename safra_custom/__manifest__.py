# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ordem de Serviço - Requisições de Itens',
    'description': """
        Altera o modulo repair para controlar a requisição de itens e suas devoluções
    """,
    'version': '1.0',
    'category': 'Repair',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Mauricio Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'base', 'repair', 'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_request_itens_menu.xml',
        'reports/report_request_itens.xml',
        # 'reports/report_saleorder_safra.xml',
        'views/repair_view.xml',
    ],
    'demo': [],
    'installable': True,
}
