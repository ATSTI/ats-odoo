from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    residence_id = fields.Many2one(
        'condo.residence', string='Residência'
    )
    condo_residence_ids = fields.Many2many(
        comodel_name="condo.residence",
        relation="residence_partner_rel",
        column1="partner_id",
        column2="residence_id",
        string="Residências"
    )

    visitor_ids = fields.One2many(
        'condo.visitor',
        'residence_id',
        string="Visitantes"
    )

    is_morador = fields.Boolean(
        string="É Morador",
        compute="_compute_is_morador",
        store=True
    )

    @api.depends('condo_residence_ids.partner_ids')
    def _compute_is_morador(self):
        all_morador_ids = self.env['condo.residence'].search([]).mapped('partner_ids.id')
        for partner in self:
            partner.is_morador = partner.id in all_morador_ids