# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fechamento de Caixa',
    'version': '16.0.1.0.0',
    'category': 'Point Of Sale',
    'license': 'AGPL-3',
    'sequence': 10,
    'summary': 'Gerenciamento e fechamento de caixas POS',
    'description': """
Fechamento de Caixa
====================

Este módulo adiciona funcionalidades para controle e fechamento de caixa em sessões POS.

Funcionalidades:
- Registro de fechamento de caixa com cálculo automático de valores;
- Controle de sangrias, saldo inicial e saldo final;
- Campos de análise e aprovação;
- Controle de permissões de alteração de estado (rascunho, feito, aprovado);
- Registro de observações e motivos.
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['point_of_sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/fechar_caixa.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
