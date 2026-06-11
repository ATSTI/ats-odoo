# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Banco Inter - adicionando desconto por cliente",
    "summary": """
        Adicionando desconto por cliente para boletos do Banco Inter""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ATSTi,",
    "website": "https://github.com/OCA/l10n-brazil",
    "maintainers": ["crsilveira"],
    "development_status": "Alpha",
    "depends": [
        "l10n_br_account",
        "l10n_br_bank_api_inter",
    ],
    "data": [       
        "views/res_partner.xml",
    ],
    "demo": [
    ],
}
