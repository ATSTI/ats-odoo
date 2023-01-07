# © 2016 Danimar Ribeiro, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Pagamentos via Boleto Bancário',
    'summary': """""",
    'description': """Permite gerar e realizar a integração bancária através de
        da API Banco INTER""",
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.trustcode.com.br',
    'contributors': [
        'Danimar Ribeiro <danimaribeiro@gmail.com>',
    ],
    'depends': [
        'br_account_payment', 'br_data_account_product','br_boleto',
    ],
    'data': [
        'views/account_journal.xml',
        'views/account_move_line.xml',
    ],
    'installable': True,
    'application': True,
}
