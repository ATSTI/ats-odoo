# Copyright (C) 2020 - Carlos R. Silveira - ATSti Soluções
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Sped EFD ICMS/IPI",
    "summary": """ Sped EFD ICMS/IPI - com localização: OCA/l10n-brazil """,
    "version": "14.0.1.0.0",
    "category": "Localisation",
    "author": 'Carlos R. Silveira, ATSti Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos R. Silveira<carlos@atsti.com.br>',
    ],
    'depends': [
        'l10n_br_fiscal',
        'l10n_br_nfe',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sped_icms_ipi_view.xml',
    ],
    'demo': [],
    'installable': True,
}
