# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Pagamentos via API Boleto Bancário - Bradesco',
    'summary': """""",
    'description': """Permite gerar e realizar a integração bancária através de
        da API Banco Bradesco""",
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'ATSTi',
    'license': 'AGPL-3',
    'website': '',
    'contributors': [
        'Carlos Silveira <crsilveira@gmail.com>',
    ],
    'depends': [
        'br_account_payment', 'br_data_account_product','br_boleto',
    ],
    'data': [
        'views/account_journal.xml',
        # 'views/account_move_line.xml',
    ],
    'installable': True,
    'application': False,
}
