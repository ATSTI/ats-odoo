
# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Urgent'),
]


class RepairStage(models.Model):
    _name = 'repair.stage'
    _description = 'Estagio da ordem de reparo'
    _order = 'sequence, name, id'

    name = fields.Char(string='Nome', required=True)
    sequence = fields.Integer('Sequencia', default=1,
                              help="Used to order stages. Lower is better.")
    legend_priority = fields.Text('Legenda',
                                  translate=True,
                                  help='Explanation text to help users using'
                                       ' the star and priority mechanism on'
                                       ' stages or orders that are in this'
                                       ' stage.')
    fold = fields.Boolean('Dobra',
                          help='This stage is folded in the kanban view when '
                               'there are no record in that stage to display.')
    is_closed = fields.Boolean('Estagio Fechado',
                               help='Services in this stage are considered '
                                    'as closed.')
    is_default = fields.Boolean('Estagio padrão',
                                help='Used a default stage')
    custom_color = fields.Char("Cor do Codígo", default="#FFFFFF",
                               help="Use Hex Code only Ex:-#FFFFFF")
    description = fields.Text(translate=True)
    stage_type = fields.Selection([('order', 'Order'),
                                   ('equipment', 'Equipamento'),
                                   ('location', 'Lugar'),
                                   ('worker', 'Trabalho')], 'Type',
                                  required=True)
    company_id = fields.Many2one(
        'res.company', string='Empresa'
    )

    @api.multi
    def get_color_information(self):
        # get stage ids
        stage_ids = self.search([])
        color_information_dict = []
        for stage in stage_ids:
            color_information_dict.append({
                'color': stage.custom_color,
                'field': 'stage_id',
                'opt': '==',
                'value': stage.name,
            })
        return color_information_dict

    @api.model
    def create(self, vals):
        stages = self.env['repair.stage'].search([])
        for stage in stages:
            if stage.stage_type == vals['stage_type'] and \
               stage.sequence == vals['sequence']:
                raise ValidationError(_("Cannot create FSM Stage because "
                                        "it has the same Type and Sequence "
                                        "of an existing FSM Stage."))
        return super(RepairStage, self).create(vals)

    @api.constrains('custom_color')
    def _check_custom_color_hex_code(self):
        if self.custom_color and not self.custom_color.startswith(
                '#') or len(self.custom_color) != 7:
            raise ValidationError(
                _('Color code should be Hex Code. Ex:-#FFFFFF'))