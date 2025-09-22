from odoo import models, fields

class Repair(models.Model):
    _inherit ='repair.order'

    date_repair = fields.Date("Data do reparo")