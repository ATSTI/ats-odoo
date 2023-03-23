# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models, _


class RepairVehicle(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'repair.vehicle'
    _description = 'Vehicle'
    _order = 'placa asc, acquisition_date asc'

    name = fields.Char("Veículo")
    description = fields.Text("Descrição")
    active = fields.Boolean('Active', default=True, tracking=True)
    acquisition_date = fields.Date('Data de aquisiçao', required=False,
        default=fields.Date.today, help='Date when the vehicle has been immatriculated')
    placa = fields.Char(tracking=True, string="Placa",
        help='License plate number of the vehicle (i = plate number for a car)')
    modelo = fields.Char("Modelo do veículo")
    ano = fields.Char("Ano/Modelo do veículo")
    partner_id = fields.Many2one(
        'res.partner', 'Cliente',
        index=True,
    )
    repair_ids = fields.One2many(
        "repair.order",
        "vehicle_id",
        string="Ordem Serviço",
        copy=False, readonly=True
    )