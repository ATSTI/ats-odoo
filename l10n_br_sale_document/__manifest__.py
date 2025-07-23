# Copyright 2022 ATSTi Soluções
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Brazilian Localization DANFE Document in Sale Order",
    "summary": """
        Geração do documento DANFE para pedidos de venda.
        Para UF São Paulo funciona normal,
        alguns UFs não possuem a busca.""",
    "version": "14.0.2.0.2",
    "license": "AGPL-3",
    "author": "ATSTi,Odoo Community Association (OCA)",
    "maintainers": ["carlos"],
    "website": "",
    "depends": ["l10n_br_base", "l10n_br_nfe", "l10n_br_account_nfe"],
    "data": [
        "views/relatorio_danfe.xml",
        "views/sale_view.xml",
    ],
    "demo": [
    ],
}
