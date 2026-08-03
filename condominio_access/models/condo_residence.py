from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class CondoResidence(models.Model):
    _name = "condo.residence"
    _description = "Residências do Condomínio"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ticket_ids = fields.One2many(
    "helpdesk.ticket",
    "residence_id",
    string="Chamados",
)

    helpdesk_ticket_count = fields.Integer(
    compute="_compute_helpdesk_ticket_count")

    helpdesk_ticket_active_count = fields.Integer(
    compute="_compute_helpdesk_ticket_count")  

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

    logs_ids = fields.One2many(
        "condo.residence.logs",
        "residence_id",
        string="Logs"
    )

    is_water_reader = fields.Boolean(
    compute="_compute_is_water_reader")

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

    lote = fields.Char(string="Quadra/Lote" ,tracking = True)

    moradores = fields.Integer(
        string="Moradores", compute='_compute_moradores', store=True
    )

    tipo = fields.Selection([
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento')
    ], string="Tipo")

    active = fields.Boolean(string="Ativo", default=True)

    image_1920 = fields.Image("Imagem")

    inquilino_id = fields.Many2one(
    comodel_name="res.partner",
    string="Inquilino")

    proprietario_id = fields.Many2one(
    comodel_name="res.partner",
    string="Proprietário")

    coproprietario_id = fields.Many2one(
    comodel_name="res.partner",
    string="Co-Proprietário")

    visitantes_recorrentes_ids = fields.One2many(
    "condo.recurring.visitor",
    "residence_id",
    string="Visitantes Recorrentes")

    def _compute_is_water_reader(self): 
        for rec in self:
            rec.is_water_reader = self.env.user.has_group(
                'condominio_access.group_condo_water_reader')

    @api.depends('lote','proprietario_id')
    def _compute_name(self):
        for rec in self:           
            rec.name = f"{rec.lote} - {rec.proprietario_id.name if rec.proprietario_id else 'Sem Proprietário'}"

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
                    _("Já existe uma residência cadastrada no lote %s.") % record.lote)
            
    def write(self, vals):
        if self.env.user.has_group(
            'condominio_access.group_condo_water_reader'):
            campos_permitidos = {
                'leitura_agua_ids',
            }
            campos_invalidos = set(vals.keys()) - campos_permitidos
            if campos_invalidos:
                raise UserError(
                    _("Você só pode editar leituras de água."))
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
       
    def action_open_import_water(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "condo.import.water.wizard",
            "view_mode": "form",
            "target": "new",
        }
    
    def action_compute_name(self):
        residences = self.env['condo.residence'].search([])
        for rec in residences:
            rec._compute_name()

    def _compute_helpdesk_ticket_count(self):
        Ticket = self.env["helpdesk.ticket"]

        for rec in self:
            tickets = Ticket.search([
                ("residence_id", "=", rec.id)
            ])

            rec.helpdesk_ticket_count = len(tickets)
            rec.helpdesk_ticket_active_count = len(
                tickets.filtered(lambda t: not t.stage_id.is_close)
            )

    def action_view_helpdesk_tickets(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Chamados",
            "res_model": "helpdesk.ticket",
            "view_mode": "tree,form",
            "domain": [("residence_id", "=", self.id)],
            "context": {
                "default_residence_id": self.id,
            },
        }

    # def action_clear_all_readings(self):
    #     readings = self.env["condo.water.reading"].search([])
        
    #     if readings:
    #         readings.unlink()

    #     return {
    #         "type": "ir.actions.client",
    #         "tag": "display_notification",
    #         "params": {
    #             "title": "Concluído",
    #             "message": "Todas as leituras foram removidas.",
    #             "type": "success",
    #             "sticky": False,
    #         }
    #     }
