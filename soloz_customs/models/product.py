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

class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def write(self, vals):
        for rec in self:
            mensagens = []

            for key, value in vals.items():
                field = rec._fields[key]

                # Many2one
                if isinstance(field, fields.Many2one):
                    old_name = rec[key].name
                    new_name = self.env[field.comodel_name].browse(value).name
                    mensagens.append(f"{field.string}: {old_name} --> {new_name}")

                # Boolean
                elif isinstance(value, bool):
                    mensagens.append(f"{field.string}: {rec[key]} --> {value}")

                # Int/Float/Char/Outros
                else:
                    mensagens.append(f"{field.string}: {rec[key]} --> {value}")

            if mensagens:
                # Posta no chatter
                rec.message_post(body="<br/>".join(mensagens))

        return super().write(vals)

