# Copyright (C) 2025 - ATSTi
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Edição de Parceiros no Site',
    'version': '1.0',
    'category': 'website',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Cadastro já existente pode ser editado atráves do formulário do site',
    'description': """
        Com esse módulo, se um parceiro já existir com o mesmo CNPJ/CPF informado no formulário do site, ao invés de criar um novo cadastro, o sistema irá atualizar os dados do parceiro existente (exceto nome e CNPJ/CPF).
    """,
    'author': 'ATSTi Soluções',
    'maintainer': 'Carlos R. Silveira, Mauricio-ATS, ATSTi',
    'website': 'https://github.com/ATSTI/ats-odoo',
    'depends': ['website', 'sale', 'website_sale', 'l10n_br_base'],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
