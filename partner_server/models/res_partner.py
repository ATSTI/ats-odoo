from odoo import models, fields, api

class Partner(models.Model):
    _inherit = 'res.partner'

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
        



    



   