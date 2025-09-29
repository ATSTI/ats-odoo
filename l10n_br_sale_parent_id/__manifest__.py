# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Sale Order - Faturamento com Cliente Pai',
    'version': '16.0.1.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'sequence': 7,
    'summary': 'Ao gerar fatura, usa o cliente pai como destinatário e mantém referência ao filho',
    'description': """
        Este módulo ajusta o comportamento da geração de faturas a partir de pedidos de venda:
        
        - O dicionário fiscal é atualizado automaticamente através de `_prepare_br_fiscal_dict()`;
        - Caso o cliente possua um cliente pai configurado, a fatura é emitida para o pai (`partner_id`);
        - A referência (`ref`) da fatura é preenchida com o nome do cliente filho.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['sale_management', 'l10n_br_fiscal',],
    'data': [
        # Nenhum XML necessário neste módulo
    ],
    'installable': True,
    'application': False,
}