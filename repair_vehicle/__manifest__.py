# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ordem de Serviço-Veículos',
    'description': """
        Altera o modulo repair para utilizar
        para Ordemde Serviço em veículos
    """,
    'version': '1.0',
    'category': 'Repair',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'base', 'repair', 'stock', 'sale'
    ],
    'data': [
        'views/repair_stage.xml',
        'views/repair_vehicle.xml',
        'views/repair_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'installable': True,
}
