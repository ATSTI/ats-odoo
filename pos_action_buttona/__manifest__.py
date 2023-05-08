# © 2023 Carlos R. Silveira, Mauricio Silveira, ATSti Solucoes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Botão de POS',
    'version': '1.0',
    'category': 'Others',
    'sequence': 2,
    'summary': 'Colocar botão no pos',
    'description': """
        Colocar botão no pos
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['base', 'point_of_sale'],
    'qweb': [
        'static/src/xml/action_button.xml',
    ],
    'data': [
        'views/view.xml'
    ],
    'installable': True,
    'application': False,
}
