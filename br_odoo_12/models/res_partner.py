from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    city_id_bkp = fields.Many2one("res.state.city")
    cnpj_cpf_bkp = fields.Char(string="Cnpj/CPF")
    inscr_est_bkp = fields.Char(related="inscr_est", store=True)
    rg_fisica_bkp = fields.Char(related="rg_fisica", store=True)
    inscr_mun_bkp = fields.Char(related="inscr_mun", store=True)
    suframa_bkp = fields.Char(related="suframa", store=True)
    legal_name_bkp = fields.Char(related="legal_name", store=True)
    district_bkp = fields.Char(related="district", store=True)
    number_bkp = fields.Char(related="number", store=True)

    # @api.depends('city_id')
    # def _compute_city(self):
    #     for partner in self:
    #         if partner.city_id:
    #             partner.city_id_bkp = partner.city_id