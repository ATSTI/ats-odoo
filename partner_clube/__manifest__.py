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
    "name": "Associações e Clubes",
    "description": """
        Campos adicionais para Associações e Clubes
    """,
    "version": "14.0.2.1.1",
    "category": "Localisation",
    "author": "ATS Solucoes",
    "website": "http://www.atsti.com.br",
    "license": "AGPL-3",
    "contributors": [
        "Carlos Silveira<carlos@atsti.com.br>",
    ],
    "depends": [
        "base", "l10n_br_base", "contacts",
    ],
    "data": [
        "views/partner_view.xml",
        "security/ir.model.access.csv",
        "views/partner_categoria_view.xml",
    ],
    "demo": [],
    "installable": True,
}
