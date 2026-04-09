# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, _, fields

class Partner(models.Model):

    _inherit = 'res.partner'

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

                # Many2many
                if isinstance(field, fields.Many2many):
                    old_list = rec[key].mapped('name')
                    new_list = self.env[field.comodel_name].browse(value[0][2]).mapped('name')
                    mensagens.append(f"{field.string}: {', '.join(old_list)} --> {', '.join(new_list)}")
                    

                # Boolean
                elif isinstance(value, bool):
                    mensagens.append(f"{field.string}: {rec[key]} --> {value}")

                # Selection
                elif isinstance(field, fields.Selection):
                    old_value = dict(field.selection).get(rec[key], rec[key])
                    new_value = dict(field.selection).get(value, value)
                    mensagens.append(f"{field.string}: {old_value} --> {new_value}")

                # Int/Float/Char/Outros
                else:
                    mensagens.append(f"{field.string}: {rec[key]} --> {value}")

            if mensagens:
                # Posta no chatter
                rec.message_post(body="<br/>".join(mensagens))

        return super().write(vals)

