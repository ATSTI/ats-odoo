# Copyright (C) 2025 - ATSTi
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Situação do Contrato',
    'version': '16.0.1.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'sequence': 2,
    'summary': 'Adiciona estagios no contrato',
    'description': """
        Este Módulo adiciona novas funções para o Contrato:
        - Estagios para controle do contrato
        --> Novo, Em andamento , Concluido
    """,
    'author': 'ATSTi Soluções',
    'website': '',
    'depends': ["contract"],
    'data': [
        "views/contract.xml",
    ],
    'installable': True,
    'application': False,
}

