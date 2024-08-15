# Copyright 2015 Antiun Ingenieria S.L. - Javier Iniesta
# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"
    
    tipo = fields.Selection(
        selection=[
            ('seguro', 'Seguro'),
            ('previdencia', 'Previdência'),
            ('consorcio', 'Consórcio'),
            ('saude', 'Saúde'),
            ('cartadefianca', 'Carta de Fiança'),
            ('fiancalocativa', 'Fiança Locativa'),
            ('emprasar', 'Emprasarial'),
            ('capitali', 'Capitalização'),
            ('rc', 'RC'),
         ],
    )
    tipo_seguro = fields.Selection(
        selection=[
            ('vida', 'Seg. de Vida'),
            ('carro', 'Seg. de Carro'),
            ('casa', 'Seg. de Casa'),
            ('animais', 'Seg. de Animais'),
            ('outros', 'Outro Seg.'),
            ('cavalo', 'Cavalo'),
            ('residen', 'Residencial'),
            ('auto', 'Auto'),       
            ('dit', 'DIT'),       
        ]
    )
    forma_de_pag = fields.Selection(string="Forma de pagamento",
        selection=[
            ('deb', 'Debito'),
            ('cred', 'Credito'),
            ('bole', 'Boleto'),
         ],
    )
    
    valorl = fields.Float('Valor Liquido')
    comissao = fields.Float('Comissao')
    cod_seguro = fields.Char('Placa/Nome')
    corretora_id = fields.Many2one(
        comodel_name="res.partner",
        string="Seguradora/Administradora",
    )
    vencimentos = fields.Date(
        string="Data vencimento",
    )
    apolice = fields.Char('Apolice')