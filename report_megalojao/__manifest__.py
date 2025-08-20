# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio de Orçamento (Fatura)',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'relatorios de orçamento para o Megalojao',
    'description': """
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account', 'report_cabecalho'],
    'data': [
        'report/report_orcamento_megalojao.xml',
        'views/report_relatorios.xml',
    ],
    'installable': True,
    'application': False,
}
