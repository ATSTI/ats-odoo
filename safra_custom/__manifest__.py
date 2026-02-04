# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Transação de Materiais Internos',
    'description': """
        Módulo que permite o controle da transação de itens internos
    """,
    'version': '1.0',
    'category': 'Others',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Mauricio Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'base', 'account', 'stock'
    ],
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'reports/report_request_itens_menu.xml',
        'reports/report_request_itens.xml',
        # 'reports/report_saleorder_safra.xml',
        'views/itens_view.xml',
    ],
    'demo': [],
    'installable': True,
}
