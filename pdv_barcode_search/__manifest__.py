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
    "name": "BARCODE SEARCH PDV",
    "version": "14.0.1.0.0",
    "summary": "Adiciona busca por código de barras na tela de produtos do POS",
    "description": """
        Este módulo adiciona a funcionalidade de busca por código de barras na tela de produtos do POS
        permitindo adicionar produtos rapidamente através do leitor de código de barras.
    """,
    "category": "Point of Sale",
    "license": "AGPL-3",
    "depends": ["point_of_sale",'account','sale','product'],
    'contributors': [
        'Otávio Andretta<otavio12257@gmail.com>',
    ],
    "data": [
        "views/assets.xml",           
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
