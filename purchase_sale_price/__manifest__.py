# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Definir Preco Venda',
    'version': '1.0',
    'category': 'Others',
    'summary': 'Opção para definir preço de Venda.',
    'description': """
        Permite definir o preço de venda 
        usando por base os itens do
        pedido de compra.

    """,
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Otávio Silveira Munhoz <otaviosilmunhoz@hotmail.com>',
    ],
    'depends': [
        'purchase','product_sale_margin'
    ],
    'data': [
        'views/purchase_itens_view.xml',
        'views/purchase_views.xml',
    ],
    'demo': [],
    'installable': True,
}
