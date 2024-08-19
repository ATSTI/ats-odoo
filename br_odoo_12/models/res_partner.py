from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    city_id_bkp = fields.Many2one("res.state.city")
    cnpj_cpf_bkp = fields.Char(string="Cnpj/CPF")
    inscr_est_bkp = fields.Char(string="inscr_est")
    rg_fisica_bkp = fields.Char(string="rg_fisica")
    inscr_mun_bkp = fields.Char(string="inscr_mun")
    suframa_bkp = fields.Char(string="suframa")
    legal_name_bkp = fields.Char(string="legal_name")
    district_bkp = fields.Char(string="district")
    number_bkp = fields.Char(string="number")

    # @api.depends('city_id')
    # def _compute_city(self):
    #     for partner in self:
    #         if partner.city_id:
    #             partner.city_id_bkp = partner.city_id