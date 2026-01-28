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
    "name": "POS CUSTOM A PRAZO",
    "version": "14.0.1.0.0",
    "summary": "Adiciona um botão Vendas a prazo na tela de pagamento do POS",
    "description": """
        Este módulo adiciona um botão chamado 'Venda a prazo' na tela de pagamento do POS
        que permite faturar o pedido sem emissao fiscal, registrando pagamentos parciais ou totais.
        Permite controle de vendas 'fiado'. Também adiciona um botão de Dados adicionais que é impresso junto do recibo não fiscal do PDV
    """,
    "category": "Point of Sale",
    "author": "Você",
    "website": "https://seusite.com",
    "license": "AGPL-3",
    "depends": ["point_of_sale",'account','sale','product'],
    'contributors': [
        'Otávio Andretta<otavio12257@gmail.com>',
    ],
    "data": [
        "views/assets.xml",           
    ],
   'qweb': [
        'static/src/xml/OrderReceipt.xml',
    ],
    "installable": True,
    "application": False,
    "auto_install": False
}
