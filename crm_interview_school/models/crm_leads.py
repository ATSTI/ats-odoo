from odoo import api, models, fields, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    resp_name = fields.Char(string='Nome do Responsável', required=True)
    resp_ped_name = fields.Char(string='Nome do Responsável Pedagógico')
    grau_parentesco_ped = fields.Char(string='Grau de Parentesco Pedagógico')
    phone_ped = fields.Char(string='Telefone do Responsável Pedagógico')
    email_ped = fields.Char(string='Email do Responsável Pedagógico')

    resp_finan_name = fields.Char(string='Nome do Responsável Financeiro')
    grau_parentesco_finan = fields.Char(string='Grau de Parentesco Financeiro')
    phone_finan = fields.Char(string='Telefone do Responsável Financeiro')
    email_finan = fields.Char(string='Email do Responsável Financeiro')

    source_indication = fields.Char(string='Indicação')

    child_ids = fields.One2many('crm.lead.child', 'lead_id', string='Ingressantes')

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"{vals.get('resp_name', 'Sem responsável')}"

        return super().create(vals)

class CrmLeadChild(models.Model):
    _name = 'crm.lead.child'
    _description = 'Filhos do Lead'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, ondelete='cascade')
    child_name = fields.Char(string='Nome do Filho')
    # child_age = fields.Integer(string='Idade do Filho')

    tag_ids = fields.Many2many(
        'crm.tag', 'tag_id', string='Série/Nível',
        help="9º Ano, Ensino Médio, etc."
    )

    school_period = fields.Selection(
        selection=[
            ('matutino', 'Matutino'),
            ('vespertino', 'Vespertino'),
            ('integral', 'Integral'),
        ],
        string='Período Escolar'
    )

    current_school = fields.Char(string='Escola Atual')
    tuition_cost = fields.Float(string='Valor da Mensalidade')
    tuition_installments = fields.Integer(string='Número de Parcelas')
    material_cost = fields.Float(string='Valor do Material')
    material_installments = fields.Integer(string='Número de Parcelas do Material')

    discount_acquired = fields.Float(string='Desconto Adquirido')
    discount_validity_date = fields.Date(string='Validade do Desconto')

    @api.model
    def create(self, vals):
        child = super().create(vals)

        if child.lead_id and child.tag_ids:
            child.lead_id.tag_ids |= child.tag_ids

        if child.lead_id and child.tuition_cost:
            total_tuition = sum(c.tuition_cost for c in child.lead_id.child_ids)
            child.lead_id.expected_revenue = total_tuition

        return child

    def write(self, vals):
        result = super().write(vals)

        if 'tag_ids' in vals:
            for child in self:
                if child.lead_id:
                    child.lead_id.tag_ids |= child.tag_ids

        if 'tuition_cost' in vals:
            for child in self:
                if child.lead_id:
                    total_tuition = sum(c.tuition_cost for c in child.lead_id.child_ids)
                    child.lead_id.expected_revenue = total_tuition

        return result