# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatorio de comissão',
    'version': '1.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Impressão de Nota de comissão',
    'description': """
        Para que funcione é nescessario preencher no pedido de venda o campo VENDEDOR (aba, outras informações), 
        e colocar a porcentagem de comissão no campo REFERENCIA (contatos, vendas e compras) do respectivo,
        10 = 10%...
    """,
    'author': 'ATS Soluções',
    'website': '',
    'depends': ['account'],
    'data': [
        'report/account_move_service_report_templates.xml',
        'report/account_move_service_report.xml',
    ],
    'installable': True,
    'application': False,
}
