from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # city_id_bkp = fields.Many2one("res.state.city")
    ibge_code = fields.Char(string=u'IBGE Code', size=7, copy=False)
    cnpj_cpf_bkp = fields.Char(string="Cnpj/CPF")
    inscr_est_bkp = fields.Char(string="inscr_est")
    indicador_ie_dest_bkp = fields.Selection([
        ('1', u'1 - Contribuinte ICMS'), 
        ('2', u'2 - Contribuinte isento de inscrição'),
        ('9', u'9 - Não contribuinte')
        ], 'Indicaodr IE',
    )
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