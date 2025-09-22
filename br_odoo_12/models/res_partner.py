from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ibge_code = fields.Char(string='IBGE Code', size=7, copy=False)
    cnpj_cpf_bkp = fields.Char(string="Cnpj/CPF")
    inscr_est_bkp = fields.Char(string="inscr_est")
    indicador_ie_dest_bkp = fields.Selection([
        ('1', '1 - Contribuinte ICMS'), 
        ('2', '2 - Contribuinte isento de inscrição'),
        ('9', '9 - Não contribuinte')
        ], 'Indicaodr IE',
    )
    rg_fisica_bkp = fields.Char(string="rg_fisica")
    inscr_mun_bkp = fields.Char(string="inscr_mun")
    suframa_bkp = fields.Char(string="suframa")
    legal_name_bkp = fields.Char(string="legal_name")
    district_bkp = fields.Char(string="district")
    number_bkp = fields.Char(string="number")
