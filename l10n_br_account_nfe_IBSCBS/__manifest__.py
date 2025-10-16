# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'NFe Informações do IBSCBS',
    'version': '14.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 9,
    'summary': 'Insere na Nota Fiscal as informações de IBSCBS',
    'description': """
        Este módulo permite preencher e enviar notas com informações do IBSCBS:
        
        - 
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_fiscal', 'spec_driven_model', 'l10n_br_nfe','l10n_br_nfe_spec'],
    'data': [
        "data/l10n_br_fiscal.tax.group.csv",
        "data/l10n_br_fiscal.cst.csv",
        "data/l10n_br_fiscal.tax.csv",
        "views/document_view.xml",
        # "views/account_invoice_view.xml",
    ],
    "post_init_hook": "post_load_constants",
    'installable': True,
    'application': False,
}