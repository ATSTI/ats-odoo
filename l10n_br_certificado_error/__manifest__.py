# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Erro de Certificado Expirado',
    'version': '1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Certificado digital expirado',
    'description': """
        Esse módulo transparece o erro de certificado expirado para o user
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['l10n_br_nfe', 'l10n_br_fiscal_certificate'],
    'data': [
        # 'views/certificate.xml',
    ],
    'installable': True,
    'application': False,
}