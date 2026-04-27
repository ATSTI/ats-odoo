from odoo import models, fields, api

class CondoResidence(models.Model):
    _name = "condo.residence"
    _description = "Residências do Condomínio"

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
    
    visitor_ids = fields.One2many(
        "condo.visitor",
        "residence_id",
        string="Visitantes"
    )

    name = fields.Char(string="Identificação", compute ='_compute_name', store=True)

    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="residence_partner_rel",  
        column1="residence_id",
        column2="partner_id",
        string="Moradores"
    )

    rua = fields.Char(string="Rua")
    numero = fields.Char(string="Número")
    lote = fields.Char(string="Lote")

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

    total_agua = fields.Float(
    string="Total Água",
    compute="_compute_total_agua",)



    @api.depends('lote','proprietario_id')
    def _compute_name(self):
        for rec in self:           
            rec.name = f"{rec.proprietario_id.name if rec.proprietario_id else 'Sem Proprietário'} - {rec.lote}"


    @api.depends('leitura_agua_ids.valor_conta')
    def _compute_total_agua(self):
        for rec in self:
            rec.total_agua = sum(rec.leitura_agua_ids.mapped('valor_conta'))

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

