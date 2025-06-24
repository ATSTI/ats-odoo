# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FSMPerson(models.Model):
    _inherit = "fsm.person"

    @api.onchange('name')
    def _onchange_name(self):
        import pudb;pu.db
        if self.name:
            prt = self.env['res.partner'].search([
                ('name', '=', self.name),
                ('fsm_person', '=', True)
            ])
            if prt:
                self.partner_id = prt.id
    
    #TODO DENTRO DO PROPRIO FIELDSERVICE, MODIFIQUEI O SECURITY PARA QUE O USUARIO NÃO CONSIGA EDITAR UMA ORDER
