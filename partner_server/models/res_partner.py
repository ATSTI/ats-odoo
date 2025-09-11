from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

<<<<<<< HEAD
    servidor_id = fields.Many2one(
    'servidores.infos',
    string='Servidor',
    store=True
)
    porta_selection = fields.Many2one(
    'portas.server',
    string='Porta',
    store=True,
    domain="[('servidor_id', '!=', False), ('servidor_id', '=', servidor_id)]"
)
    obs_server_texto = fields.Text(
    string="Observação do Servidor",
    compute="_compute_obs_server_texto"
)
    @api.depends('servidor_id')
    def _compute_obs_server_texto(self):
        for rec in self:
            rec.obs_server_texto = rec.servidor_id.obs_server if rec.servidor_id else ''


    @api.onchange('financeiro')
    def _onchange_financeiro(self):
        if self.financeiro and self.financeiro.id != self.id:
            self.servidor_id = self.financeiro.servidor_id or False
            self.porta_selection = self.financeiro.porta_selection or False

    def action_sincronizar_servidores(self):
        for rec in self:
            dependentes = self.env['res.partner'].search([('financeiro', '=', rec.id)])
            for parceiro in dependentes:
                parceiro.servidor_id = rec.servidor_id
                parceiro.porta_selection = rec.porta_selection


class Servidor(models.Model):
    _name = 'servidores.infos'
    _description = "Informações do Servidor"

    server_name = fields.Char("Nome do Servidor")

    porta_ids = fields.One2many(
        "portas.server",
        'servidor_id',
        string='Portas',
        copy=False,
        
    )
    obs_server = fields.Text(string="Observações do Servidor")

    def name_get(self):
        result = []
        for rec in self:
            nome = rec.server_name or "Servidor sem nome"
            result.append((rec.id, nome))
        return result


    def unlink(self):
        portas = self.env['portas.server'].search([('servidor_id', 'in', self.ids)])
        portas.unlink()
        return super().unlink()

class PortaServer(models.Model):
    _name = "portas.server"
    _description = "Informações da Porta"

    nporta = fields.Char(string="Número da Porta")

    servidor_id = fields.Many2one(
        comodel_name="servidores.infos",
        string="Servidor",
    )

    def name_get(self):
        result = []
        for rec in self.filtered(lambda r: r.servidor_id):
            servidor_nome = rec.servidor_id.server_name
            descricao = f"{rec.nporta} - {servidor_nome}"
            result.append((rec.id, descricao))
        return result
        



    



   
=======
   
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
>>>>>>> 53808342506d7bb9f18524fd1279810841e2c661
