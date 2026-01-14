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
    'name': 'Visualização, Notas por Empresa',
    'version': '1.0',
    'category': '',
    'author': 'ATS Solucoes',
    'website': 'http://www.atsti.com.br',
    'license': 'AGPL-3',
    'contributors': [
        'Mauricio Silveira<maurs320@atsti.com.br>',
    ],
    'depends': [
        'base', 'sale', 'l10n_br_fiscal', 'l10n_br_account',
    ],
    'data': [
        'report/all_note_template.xml',
        'report/all_note_template_due.xml',
        'report/all_note_report_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
}

