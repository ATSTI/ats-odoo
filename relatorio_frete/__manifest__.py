# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Relatório Despesa x Receita de fretes',
    'version': '16.0',
    'category': 'Others',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Relatório Despesa x Receita de fretes',
    'description': """
        Faturas fornecedor Frete x Receitas de Frete (campo frete pedido de venda)
        utilizando os dados dos pedidos de venda relacionados aos fretes.
        Usando documentos relacionados (NFe referente aos pedidos de venda relacionadas aos fretes)
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ['account_financial_report'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/frete_report_wizard_view.xml",
        "reports.xml",
        "report/templates/frete_report.xml",
    ],
    'installable': True,
    'application': False,
}
