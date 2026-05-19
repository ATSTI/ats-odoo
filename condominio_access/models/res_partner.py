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

    residence_owner_ids = fields.One2many(
        'condo.residence',
        'proprietario_id',
        string="Residências como Proprietário"
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

    data_nascimento = fields.Date(
        string="Data de Nascimento"
    )

    @api.depends('condo_residence_ids')
    def _compute_is_morador(self):
        for partner in self:
            partner.is_morador = bool(partner.condo_residence_ids)

    def link_residence(self):
        partners = self.env['res.partner'].search([('residence_id', '!=', False), ('is_company', '=', False)])
        for prt in partners:
            for resd in prt.condo_residence_ids:
                if prt.id in resd.partner_ids.ids:
                    resd.partner_ids = [(3, prt.id)]
            prt.is_company = False
            residence = self.env['condo.residence'].search([('proprietario_id.name', '=', prt.name)])
            if len(residence) >= 1:
                for resd in residence:
                    prt.residence_id = resd.id
                    prt.condo_residence_ids = [(4, resd.id)]
