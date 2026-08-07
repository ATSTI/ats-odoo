from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import re


class CondoVisitor(models.Model):
    _name = "condo.visitor"
    _description = "Visitantes do Condomínio"
    _order = "status desc, data_entrada desc"
    _rec_name = "name"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Descrição",
        compute="_compute_name",
        store=True)

    cancel_reason = fields.Text(
    string="Justificativa da Negativa",
    readonly=True,
)

    documento = fields.Char("CPF do visitante", store = True)

    visitante_id = fields.Many2one(
    "res.partner",
    string="Visitante",
    required=True,
    domain="[('is_morador','=',False)]")

    morador_id = fields.Many2one(
    "res.partner",
    string="Morador",
    required=True,
    domain="[('is_morador','=',True)]")

    residence_partner_ids = fields.Many2many(
    "res.partner",
    compute="_compute_residence_partners")
    
    resident_partner_ids = fields.Many2many(
    "res.partner",
    related="residence_id.partner_ids",
    store=False)

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        compute="_compute_residence_id",
        store=True,
        readonly=False)

    cpf = fields.Char(
        related="visitante_id.vat",  
        string="CPF",
        store=True)

    foto = fields.Image(
        related="visitante_id.image_1920",
        string="Foto")

    data_entrada = fields.Datetime(string="Entrada")

    data_saida = fields.Datetime(string="Saída")

    autorizado_por = fields.Many2one(
        "res.partner",
        string="Autorizado por",
        required=True)

    status = fields.Selection([
        ('esperado', 'Esperado'),
        ('presente', 'Presente'),
        ('saiu', 'Saiu'),
        ('cancelado', 'Cancelado')
    ], default='esperado', string="Status")

    tempo_permanencia = fields.Float(
        string="Tempo (h)",
        compute="_compute_tempo_permanencia")


    modelo = fields.Char("Modelo")
    placa = fields.Char("Placa")
    cor = fields.Char("Cor")


    # def formatar_cpf(valor):
    #     apenas_numeros = re.sub(r'\D', '', str(valor))
    #     cpf_com_11 = apenas_numeros.zfill(11)
    #     return f"{cpf_com_11[:3]}.{cpf_com_11[3:6]}.{cpf_com_11[6:9]}-{cpf_com_11[9:]}"


    @api.onchange("documento")
    def _compute_visitante_id(self):
        for rec in self:
            visitante = False
            if rec.documento:
                doc_limpo = "".join(c for c in rec.documento if c.isdigit())
                if len(doc_limpo) == 11:
                    doc_original = re.sub(
                        r"(\d{3})(\d{3})(\d{3})(\d{2})",
                        r"\1.\2.\3-\4",
                        doc_limpo,
                    )
                elif len(doc_limpo) == 14:
                    doc_original = re.sub(
                        r"(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})",
                        r"\1.\2.\3/\4-\5",
                        doc_limpo,
                    )
                else:
                    doc_original = rec.documento

                visitante = self.env["res.partner"].search([
                    "|",
                    ("vat", "=ilike", doc_original),
                    ("vat", "=ilike", doc_limpo),
                ], limit=1)

            rec.visitante_id = visitante



    def _default_residence_partners(self):
        Residence = self.env["condo.residence"]
        return Residence.search([]).mapped("partner_ids").ids

    @api.depends("visitante_id", "morador_id", "status")
    def _compute_name(self):
        for rec in self:
            nome = rec.visitante_id.name if rec.visitante_id else "Visitante"
            if rec.morador_id:
                nome += f" → {rec.morador_id.name}"
            if rec.status:
                nome += f" [{rec.status}]"
            rec.name = nome

    def _compute_residence_partners(self):
        Residence = self.env["condo.residence"]
        partners = Residence.search([]).mapped("partner_ids")
        for rec in self:
            rec.residence_partner_ids = partners
    
    def _default_residence_partners(self):
        Residence = self.env["condo.residence"]
        return Residence.search([]).mapped("partner_ids").ids

    @api.depends('data_entrada', 'data_saida')
    def _compute_tempo_permanencia(self):
        for rec in self:
            if rec.data_entrada:
                fim = rec.data_saida or fields.Datetime.now()
                delta = fim - rec.data_entrada
                rec.tempo_permanencia = delta.total_seconds() / 3600
            else:
                rec.tempo_permanencia = 0

    def action_entrada(self):
        for rec in self:
            visitante = rec.visitante_id
            if not visitante.vat:
                raise UserError(
                    "Para dar entrada, o visitante precisa ter:\n"  
                    "- CPF\n"
                )
            rec.status = 'presente'
            rec.data_entrada = fields.Datetime.now()

    def action_saida(self):
        for rec in self:
            rec.status = 'saiu'
            rec.data_saida = fields.Datetime.now()

    def action_cancelado(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Cancelar visita",
            "res_model": "condo.visitor.cancel.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_visitor_id": self.id,
            },
        }


    @api.onchange('visitante_id')
    def _onchange_visitante_negado(self):
        if not self.visitante_id:
            return

        ultima_negada = self.env['condo.visitor'].search([
            ('visitante_id', '=', self.visitante_id.id),
            ('status', '=', 'cancelado'),
            ('cancel_reason', '!=', False),
        ], order='id desc', limit=1)

        if ultima_negada:
            return {
                'warning': {
                    'title': 'Visitante já foi negado',
                    'message': (
                        f'Este visitante já teve uma entrada negada.\n\n'
                        f'Justificativa:\n{ultima_negada.cancel_reason}'
                    ),
                }
            }

    @api.constrains('data_saida', 'data_entrada')
    def _check_datas(self):
        for rec in self:
            if rec.data_saida and rec.data_entrada:
                if rec.data_saida < rec.data_entrada:
                    raise ValidationError("A saída não pode ser antes da entrada.")

    #TODO filtrar o campo residencia com base no campo MORADOR, para que o usuário não precise selecionar a residência manualmente.
    @api.depends("morador_id")
    def _compute_residence_id(self):
        Residence = self.env["condo.residence"]
        for rec in self:
            residence = Residence.search([
                ("partner_ids", "in", rec.morador_id.id)
            ], limit=1)
            rec.residence_id = residence

    @api.onchange('status')
    def _onchange_status(self):
        if self.status == 'presente' and not self.data_entrada:
            self.data_entrada = fields.Datetime.now()
        if self.status == 'saiu' and not self.data_saida:
            self.data_saida = fields.Datetime.now()

    @api.onchange('visitante_id')
    def _onchange_visitante_recorrente(self):
        if not self.visitante_id:
            return

        residencias = self.env['condo.residence'].search([
            ('visitantes_recorrentes_ids.partner_id', '=', self.visitante_id.id)
        ])

        if not residencias:
            return

        if len(residencias) == 1:
            residencia = residencias[0]
            recorrente = residencia.visitantes_recorrentes_ids.filtered(
                lambda r: r.partner_id == self.visitante_id
            )[:1]

            self.residence_id = residencia
            self.morador_id = recorrente.morador_id
            self.autorizado_por = recorrente.autorizado_por

        nomes = ", ".join(residencias.mapped('name'))
        return {
            'warning': {
                'title': 'Visitante Recorrente',
                'message': (
                    f'{self.visitante_id.name} já está cadastrado '
                    f'como visitante recorrente em: {nomes}'
                )
            }
        }