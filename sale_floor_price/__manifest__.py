# -*- coding: utf-8 -*-
##############################################################################
# COMO USAR A DINAMICA PARA BLOQUEAR O USUARIO DE VER O CUSTO DO PRODUTO E
# OCULTAR O BOTAO DE CRIAÇÃO DE FATURA E EDIÇÃO:
# 1- DUPLICAR O GRUPO FATURAMENTOS E REMOVER A PERMISSÃO DE EDIÇÃO E CRIAÇÃO DOS ACESSOS QUE TENHAM "FATURA" ou "LINHAS DA FATURA"
# 2- CRIAR EM IDENTIFICADORES EXTERNOS (tecnico) DO GRUPO CRIADO NO PASSO 1, O IDENTIFICADOR EXTERNO: account_move.grupo_permissao_especifica
    # -modulo = account.account_move
    # -identificador externo = grupo_permissao_especifica
    # -nome do modelo = res.groups
#  - COM ESSE PASSO E ESSE MÓDULO NÃO DEVE MAIS APARECE O CUSTO DO PRODUTO PARA OS USUÁRIOS DESSE GRUPO
##############################################################################
{
    'name' : 'Floor price on product',
    'version' : '5.1',
    'author' : "Camptocamp,Odoo Community Association (OCA)",
    'maintainer': 'Camptocamp',
    'category': 'Tool',
    'summary': """
        Set a minimal price on product and raise a warning if sale price is too low
    """,
    'website': 'http://www.camptocamp.com',
    'depends' : [
        'base',
         'stock',
         'product',
         'sale', 
    ],
    'data': [
        'views/product_view.xml',
        'views/partner_view.xml',
        # 'security/res_groups.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False
}
