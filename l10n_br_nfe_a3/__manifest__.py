# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'NFe - Emissão sem Certificado A3',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 5,
    'summary': 'Permite emissão de NFe/NFCe sem certificado digital A3 configurado',
    'description': """
        Este módulo permite que em situações onde não há certificado digital A3
        configurado na empresa, a emissão de NFe/NFCe prossiga sem erro.
        
        Funcionalidades:
        - Ajuste automático de horário da NFCe;
        - Permite exportar XML sem certificado, quando aplicável;
        - Evita erros em processos multi-company.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': [
        'l10n_br_fiscal',
        'erpbrasil.assinatura'
    ],
    'data': [
    ],
    'installable': True,
    'application': False,
}
