from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo import _

class CondoResidence(models.Model):
    _name = "condo.residence"
    _description = "Residências do Condomínio"
    _inherit = ['mail.thread', 'mail.activity.mixin']  # ← adicionar isso

    leitura_agua_ids = fields.One2many(
        "condo.water.reading",
        "residence_id",
        string="Leituras de Água"
    )
        
    tag_ids = fields.One2many(
        "condo.residence.tags",
        "residence_id",
        string="Tags"
    )

    pet_ids = fields.One2many(
        "condo.residence.pets",
        "residence_id",
        string="Pets"
    )
    
    visitor_ids = fields.One2many(
        "condo.visitor",
        "residence_id",
        string="Visitantes"
    )

    vehicle_ids = fields.One2many(
        "condo.residence.vehicles",
        "residence_id",
        string="Veículos"
    )

    is_water_reader = fields.Boolean(
    compute="_compute_is_water_reader"
)

    name = fields.Char(string="Identificação", compute ='_compute_name', store=True)

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="residence_partner_rel",  
        column1="residence_id",
        column2="partner_id",
        string="Moradores"
    )

    rua = fields.Char(string="Rua", tracking = True)
    numero = fields.Char(string="Número" ,tracking = True)
    lote = fields.Char(string="Lote" ,tracking = True)

    moradores = fields.Integer(
        string="Moradores", compute='_compute_moradores', store=True
    )

    tipo = fields.Selection([
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento')
    ], string="Tipo")

    active = fields.Boolean(string="Ativo", default=True)

    # image_128 = fields.Image("Imagem", max_width=1000, max_height=1000)
    image_1920 = fields.Image("Imagem")


   
    # avatar_128 = fields.Image(related="image_1920", max_width=128, max_height=128, store=True)

    inquilino_id = fields.Many2one(
    comodel_name="res.partner",
    string="Inquilino"
)
    
    proprietario_id = fields.Many2one(
    comodel_name="res.partner",
    string="Proprietário"
)
    
    coproprietario_id = fields.Many2one(
    comodel_name="res.partner",
    string="Co-Proprietário"
)
    
    


    visitantes_recorrentes_ids = fields.One2many(
    "condo.recurring.visitor",
    "residence_id",
    string="Visitantes Recorrentes"
)


    def _compute_is_water_reader(self): 
        for rec in self:
            rec.is_water_reader = self.env.user.has_group(
                'condominio_access.group_condo_water_reader'
            )
    @api.depends('lote','proprietario_id')
    def _compute_name(self):
        for rec in self:           
            rec.name = f"{rec.lote} - {rec.proprietario_id.name if rec.proprietario_id else 'Sem Proprietário'}"

    
    def action_compute_name(self):
        residences = self.env['condo.residence'].search([])

        for rec in residences:
            rec._compute_name()


    @api.onchange('inquilino_id')
    def _onchange_inquilino_id(self):
        for rec in self:
            if rec.inquilino_id:
                if self.inquilino_id.parent_id:
                    rec.partner_ids = [(6, 0, [rec.inquilino_id.id, rec.inquilino_id.parent_id.id])]
                else:   
                    rec.partner_ids = [(6, 0, [rec.inquilino_id.id])]
            else:
                rec.partner_ids = [(5, 0, 0)]
    
    @api.depends('partner_ids')
    def _compute_moradores(self):
        for rec in self:
            rec.moradores = len(rec.partner_ids)
    

    @api.constrains("lote")
    def _check_unique_lote(self):
        for record in self:
            if not record.lote:
                continue

            existing = self.search([
                ("id", "!=", record.id),
                ("lote", "=", record.lote),
            ], limit=1)

            if existing:
                raise ValidationError(
                    _("Já existe uma residência cadastrada no lote %s.") % record.lote
                )
    def write(self, vals):

        if self.env.user.has_group(
            'condominio_access.group_condo_water_reader'
        ):

            campos_permitidos = {
                'leitura_agua_ids',
            }

            campos_invalidos = set(vals.keys()) - campos_permitidos

            if campos_invalidos:
                raise UserError(
                    _("Você só pode editar leituras de água.")
                )

        return super().write(vals)
    
    def action_open_water_report_wizard(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Relatórios Água",
            "res_model": "condo.water.report.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_residence_id": self.id,
            }
        }   
