# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Data na Ordem de Reparo',
    'description': """
        Adiciona campo data à Ordem de reparo
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
        'repair'
    ],
    'data': [
        'views/repair_date.xml',
    ],
    'demo': [],
    'installable': True,
}
