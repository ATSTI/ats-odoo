# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Partner(models.Model):

    _inherit = 'res.partner'

    def write(self, vals_list):
        if not self.user_id and 'user_id' in vals_list:
            return super().write(vals_list)
        if 'user_id' in vals_list:
            if self.user_id != self.env.user and not self.env.user.has_group('sales_team.group_sale_manager'):
                raise UserError(_("Você não pode alterar o campo Vendedor do Contato se este não for seu, ou você não for Administrador de Vendas"))
        return super().write(vals_list)

