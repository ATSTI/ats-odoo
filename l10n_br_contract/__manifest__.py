# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ATS --> TENTANDO INSTALAR E FUNCIONAR O MODULO BANK_INTER NO ODOO 18 E ESSE MODULO DEPENDE DESTE AQUI,
#  QUE POR SUA VEZ NÃO EXISTE NO l10n-brazil 18.

{
    "name": "Brazilian Localization Contract",
    "summary": """
        Customization of Contract module for implementations in Brazil.""",
    "version": "18.0.5.1.0",
    "license": "AGPL-3",
    "author": "KMEE,Odoo Community Association (OCA)",
    "maintainers": ["mileo", "marcelsavegnago"],
    "website": "https://github.com/OCA/l10n-brazil",
    "depends": ["l10n_br_account", "contract"],
    "data": [
        "data/company.xml",
        "views/res_company.xml",
        "views/contract_view.xml",
        "views/contract_line.xml",
    ],
    "demo": [
        "demo/company.xml",
        "demo/contract_demo.xml",
    ],
}
