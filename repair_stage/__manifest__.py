# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Estágio na Ordem de Serviço',
    'description': """
        Adiciona kanban de estágio na OS
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
        'security/ir.model.access.csv',
        'views/repair_stage_data.xml',
        'views/repair_stage.xml',
        'views/repair_view.xml',
    ],
    'demo': [],
    'installable': True,
}