from odoo import fields, models, api

class PartnerEquipamento(models.Model):
    _name = 'partner.equipamento'
    _description = 'Equipamentos do Cliente'

    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
    'product.product',
    string='Equipamento',
    required=True,
    domain="[('usado','=',False)]"
)
    estado = fields.Selection([
        ('otima', 'Ótima'),
        ('bom', 'Bom'),
        ('medio', 'Médio'),
        ('ruim', 'Ruim'),
        ('pessimo', 'Péssimo'),
    ], string='Estado', compute ='_compute_estado')

    is_loan = fields.Boolean(string='Emprestado')
    data_entrada = fields.Date(string='Data de Entrada')
    data_saida = fields.Date(string='Data de Saída')
    motivo = fields.Char(string='Motivo')

    tipo = fields.Selection(
    [
        ('bcd', 'BCD'),
        ('suit', 'SUIT'),
    ],
    string='Tipo',
    compute='_compute_tipo',
    store=True
)
    obs = fields.Text(string='Observações')
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.product_id:
            record.product_id.usado = True
        return record
    def write(self, vals):
        for rec in self:
            old_product = rec.product_id
            res = super().write(vals)
            new_product = rec.product_id
            if 'product_id' in vals:
                if old_product and old_product != new_product:
                    old_product.usado = False

                if new_product:
                    new_product.usado = True
            return res
    def unlink(self):
        for rec in self:
            if rec.product_id:
                rec.product_id.usado = False

        return super().unlink()

    @api.depends('product_id', 'product_id.categ_id')
    def _compute_tipo(self):
        for rec in self:
            rec.tipo = False

            if not rec.product_id or not rec.product_id.categ_id:
                continue

            categ_name = rec.product_id.categ_id.name.upper()

            if categ_name == 'BCD':
                rec.tipo = 'bcd'
            elif categ_name == 'SUIT':
                rec.tipo = 'suit'

    
    @api.depends('product_id','product_id.situacao')
    def _compute_estado(self):
        for rec in self:
            rec.estado = False
            if not rec.product_id or not rec.product_id.situacao:
                continue
            categ_name = rec.product_id.situacao.upper()

            if categ_name =='OTIMA':
                rec.estado = 'otima'
            elif categ_name =='BOM':
                rec.estado ='bom'
            elif categ_name =='MEDIO':
                rec.estado ='medio'
            elif categ_name =='RUIM':
                rec.estado ='ruim'
            elif categ_name =='PESSIMO':
                rec.estado ='pessimo'



