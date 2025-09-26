# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Fiscal Document - Patch Form',
    'version': '16.0.1.0',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'sequence': 8,
    'summary': 'Ajustes na view do documento fiscal (NFe/NFCe)',
    'description': """
        Este módulo aplica ajustes na view de Documento Fiscal do Odoo Brasil:
        
        - Substitui o botão "Voltar p/ Em Digitação" por dois botões (um para voltar p/ digitação e outro para voltar p/ fatura);
        - Torna campos do documento somente leitura quando o estado do e-Doc é diferente de "em digitação";
        - Melhora a segurança de edição do documento fiscal.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio Silveira, ATSTi',
    'website': '',
    'depends': ['l10n_br_fiscal', 'l10n_br_account'],
    'data': [
        'views/account_invoice_view.xml',
        'views/document_view.xml',
    ],
    'installable': True,
    'application': False,
}