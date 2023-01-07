# © 2021 Carlos R. Silveira <ats@atsti.com.br>, ATS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{  # pylint: disable=C8101,C8103
    'name': 'Envio de NFS-e Sigiss',
    'summary': """Permite o envio de NFS-e Sigiss através das faturas do Odoo
    Mantido por ATS """,
    'description': 'Envio de NFS-e - Sigiss',
    'version': '12.0.1.0.0',
    'category': 'account',
    'author': 'Trustcode',
    'license': 'AGPL-3',
    'website': 'http://www.atsti.com.br',
    'contributors': [
        'Carlos R. Silveira , Manoel Santos <ats@atsti.com.br ',
    ],
    'depends': [
        'br_nfse',
    ],
    'data': [
        'views/br_account_service.xml',
        'views/res_company.xml',
        'reports/danfse_ginfes.xml',
        'wizard/cancel_nfes.xml',
    ],
    'installable': True,
    'application': True,
}
