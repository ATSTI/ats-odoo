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
    'name': 'Cria ordem de manutenção',
    'description' : 'Cria ordem de manutenção ao retorno de um equipamento. \
        IMPORTANTE: e necessario que o item esteja informado como equipamento.',
    'version': '1.0',
    'category': 'Stock',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Carlos Silveira<carlos@atsti.com.br>',
        'Mauricio Silveira<maurs320@atsti.com.br>',
    ],
    'depends': [
        'stock',
        'maintenance_product',
        'maintenance_picking',
    ],
    'data': [
    ],
    'demo': [],
    'installable': True,
}
