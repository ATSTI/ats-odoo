# -*- coding: utf-8 -*-
# © 2018  Carlos R. Silveira
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class Repair(models.Model):
    _inherit = 'repair.order'

    def _default_stage_id(self):
        stage_ids = self.env['repair.stage'].\
            search([('stage_type', '=', 'order'),
                    ('is_default', '=', True),
                    ('company_id', 'in', (self.env.user.company_id.id,
                                          False))],
                   order='sequence asc', limit=1)
        if stage_ids:
            return stage_ids[0]
        else:
            raise ValidationError(_(
                "You must create an FSM order stage first."))
    
    stage_id = fields.Many2one('repair.stage', string='Stage',
            track_visibility='onchange',
            index=True, copy=False,
            group_expand='_read_group_stage_ids',
            default=lambda self: self._default_stage_id())

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('stage_type', '=', 'order')]
        if self.env.context.get('default_team_id'):
            search_domain = [
                '&', ('team_ids', 'in', self.env.context['default_team_id'])
            ] + search_domain
        return stages.search(search_domain, order=order)



