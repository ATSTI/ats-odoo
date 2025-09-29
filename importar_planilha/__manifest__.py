# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Importar Planilha',
    'version': '16.0.1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Importação de Planilha',
    'description': """
        Este Módulo permite o usuário importar planilhas Excel (.xlsx) para o Odoo, facilitando a inserção em massa de dados como produtos, clientes e outros registros.
        Funcionalidades:
        - Suporte a arquivos Excel (.xlsx)
        - Mapeamento de colunas para campos do Odoo
        - Validação de dados antes da importação
        - Relatórios de importação com detalhes de sucesso e falhas
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['partner_manual_rank',],
    'data': [
        'security/ir.model.access.csv',
        'wizard/importar_view.xml',
    ],
    'installable': True,
    'application': False,
}