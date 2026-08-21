# Copyright (C) 2026 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Ligação Fiscal - Onchange Série de Documento',
    'version': '14.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': '',
    'description': """
Modulo simples que adiciona um onchange no campo tipo de documento para preencher automaticamente a série do documento de acordo com o tipo selecionado.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Otavio Andretta, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal','account'
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
}