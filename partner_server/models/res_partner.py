from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

   
    servidor = fields.Selection([
         ('h1','H1 - 46.202.149.96'),
         ('h2','H2 - 77.37.126.200'),
         ('h3','H3 - 147.79.107.83'),
         ('h4','H4 - 62.72.8.185'),
         ('h5','H5 - 103.199.187.100'),
         ('ats','AtsAdmin'),
         ('soloz','Soloz')
         ,
    ], string="Servidor",)
    obs_server = fields.Char("Observações")
    porta_ids = fields.One2many(
        'portas.server',
        'rp_id',
        string='Porta IDs',
        copy=False,
    )

    @api.onchange('financeiro')
    def _onchange_financeiro(self):        
        for rec in self:
            if rec.financeiro and rec.financeiro.name != rec.name:
                rec.servidor = rec.financeiro.servidor or ''
                rec.obs_server = rec.financeiro.obs or '' 
                rec.porta_ids = [(5, 0, 0)]  # remove os existentes
                rec.porta_ids = [
                    (0, 0, {'nporta': porta.nporta})
                    for porta in rec.financeiro.porta_ids
                ]

class PortaServer(models.Model):
    _name = "portas.server"
    _description = "Informações da porta"

    
    nporta= fields.Char(string="Número da porta")
    rp_id= fields.Many2one(comodel_name="res.partner", string="parceiros", invisible=True)
