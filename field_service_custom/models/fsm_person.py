# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class FSMPerson(models.Model):
    _inherit = "fsm.person"

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            prt = self.env['res.partner'].search([
                ('name', '=', self.name),
                ('fsm_person', '=', True)
            ])
            if prt:
                vals = {
                    'id' : prt.id,
                }
                # self.write({'partner_id': [(6,0, vals)]})
                self.partner_id = prt.id
                prt.write({'is_customer': True})
                prt.write({'is_supplier': True})

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        res = super(FSMPerson, self)._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
        # Check for args first having location_ids as default filter
        for arg in args:
            if isinstance(arg, (list)):
                if arg[0] == "location_ids":
                    # If given int search ID, else search name
                    if isinstance(arg[2], int):
                        self.env.cr.execute(
                            "SELECT person_id "
                            "FROM fsm_location_person "
                            "WHERE location_id=%s",
                            (arg[2],),
                        )
                    else:
                        arg[2] = "%" + arg[2] + "%"
                        self.env.cr.execute(
                            "SELECT id "
                            "FROM fsm_location "
                            "WHERE complete_name like %s",
                            (arg[2],),
                        )
                        location_ids = self.env.cr.fetchall()
                        if location_ids:
                            location_ids = [location[0] for location in location_ids]
                            self.env.cr.execute(
                                "SELECT DISTINCT person_id "
                                "FROM fsm_location_person "
                                "WHERE location_id in %s",
                                [tuple(location_ids)],
                            )
                    workers_ids = self.env.cr.fetchall()
                    if workers_ids:
                        preferred_workers_list = [worker[0] for worker in workers_ids]
                        return preferred_workers_list
        return res
    
    #TODO DENTRO DO PROPRIO FIELDSERVICE, MODIFIQUEI O SECURITY PARA QUE O USUARIO NÃO CONSIGA EDITAR UMA ORDER
