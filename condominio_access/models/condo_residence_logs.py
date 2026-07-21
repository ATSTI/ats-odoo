from odoo import fields, api, models
from odoo.exceptions import ValidationError

class CondoResidenceLogs(models.Model):
    _name = "condo.residence.logs"
    _description = "Modelo para receber os logs da controladora"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        compute="_compute_residence_id",
        store=True,
        readonly=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Morador",
        ondelete="cascade",
        required=True,
    )

    data_entrada = fields.Datetime(string="Entrada")

    data_saida = fields.Datetime(string="Saída")

    tempo_permanencia = fields.Float(
        string="Tempo (h)",
        compute="_compute_tempo_permanencia")
    
    status = fields.Selection(
        [("pendente", "Pendente"), ("concluido", "Concluído")],
        string="Status",
        compute="_compute_status",
        store=True,
        readonly=False
    )

    @api.constrains('data_saida', 'data_entrada')
    def _check_datas(self):
        for rec in self:
            if rec.data_saida and rec.data_entrada:
                if rec.data_saida < rec.data_entrada:
                    raise ValidationError("A saída não pode ser antes da entrada.")
                
    @api.depends('data_entrada', 'data_saida')
    def _compute_status(self):
        for rec in self:
            if rec.data_entrada and not rec.data_saida:
                rec.status = "pendente"
            elif rec.data_entrada and rec.data_saida:
                rec.status = "concluido"
            else:
                rec.status = False
                
    @api.depends("partner_id")
    def _compute_residence_id(self):
        Residence = self.env["condo.residence"]
        for rec in self:
            residence = Residence.search([
                ("partner_ids", "in", rec.partner_id.id)
            ], limit=1)
            rec.residence_id = residence

    @api.depends('data_entrada', 'data_saida')
    def _compute_tempo_permanencia(self):
        for rec in self:
            if rec.data_entrada:
                fim = rec.data_saida or fields.Datetime.now()
                delta = fim - rec.data_entrada
                rec.tempo_permanencia = delta.total_seconds() / 3600
            else:
                rec.tempo_permanencia = 0

    