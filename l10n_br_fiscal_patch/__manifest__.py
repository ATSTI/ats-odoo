# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Fiscal Patch - ICMS',
    'version': '16.0.1.0',
    'category': 'localisation',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Quando tem icms de desoneração e com código 03-Alívio do ICMS, desconta o valor do ICMS do total da nota.',
    'description': """
        Quando tem icms de desoneração e com código 03-Alívio do ICMS, desconta o valor do ICMS do total da nota.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_fiscal', 'l10n_br_nfe', 'l10n_br_nfe_spec', 'spec_driven_model'],
    'data': [
        "views/document_view.xml",
    ],
    'installable': True,
    'application': False,
}
