
from odoo import models, _, api, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    trans_ids = fields.One2many(
        "transp.frete",
        "am_id",
        string='Transportadora',
        copy=False
    )

    @api.depends("trans_ids")
    def _compute_freight(self):
        for record in self.trans_ids:
            self.invoice_incoterm_id = record.incoterm_id.id
            self.carrier_id = record.carrier_id.id

    # def button_wizard_transp(self):
    #     for move in self:
    #         ctx = {
    #             'default_am_id': move.id,
    #         }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'wizard.create.transp',
    #         'views': [(False, 'form')],
    #         'view_id': False,
    #         'target': 'new',
    #         'context': ctx,
    #     }


class TranspFrete(models.Model):
    _name = "transp.frete"
    _description = "Detalhe da Transportadora"

    incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        string="Tipo de Frete",
        help="International Commercial Terms are a series of"
        " predefined commercial terms used in international"
        " transactions.",
        required=True,
    )

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        string="Veículo",
        ondelete="restrict",
    )

    # related="carrier_id.partner_id",
    nfe40_transporta = fields.Many2one(
        comodel_name="res.partner",        
        string="Dados do transportador",
    )

    vehicle_id = fields.Many2one(
        comodel_name="l10n_br_delivery.carrier.vehicle",
        string="Veiculo",
    )
    vehicle = fields.Char("Veículo/Modelo")
    plate = fields.Char(
        string="Placa",
        size=7,
    )
    rntc_code = fields.Char(
        string="ANTT Code",
        size=32,
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="UF",
        domain="[('country_id.code', '=', 'BR')]",
    )
    am_id = fields.Many2one(
        comodel_name="account.move", 
        string="Documento"
    )
    nfe40_qVol = fields.Char(string="Quantidade")
    nfe40_esp = fields.Char(string="Espécie")
    nfe40_marca = fields.Char(string="Marca")
    nfe40_nVol = fields.Char(string="Numero volumes")
    nfe40_pesoL = fields.Float(
        string="Peso líq.(kg)",
        xsd_type="TDec_1203",
        digits=(
            12,
            3,
        ),
    )
    nfe40_pesoB = fields.Float(
        string="Peso bruto(kg)",
        xsd_type="TDec_1203",
        digits=(
            12,
            3,
        ),
    )
    message_warning = fields.Char(string="Aviso", readonly=True)

    @api.onchange("incoterm_id")
    def _onchange_incoterm_id(self):
        if self.incoterm_id:
            # import pudb;pu.db
            key = self.incoterm_id.freight_responsibility
            if key:
                if key == '0':
                    self.message_warning = "0 - Contratação do Frete por conta do Remetente (CIF)"
                elif key == '1':
                    self.message_warning = "1 - Contratação do Frete por conta do" " destinatário/remetente (FOB)"
                elif key == '2':
                    self.message_warning = "2 - Contratação do Frete por conta de terceiros"
                elif key == '3':
                    self.message_warning = "3 - Transporte próprio por conta do remetente"
                elif key == '4':
                    self.message_warning = "4 - Transporte próprio por conta do destinatário"
                elif key == '9':
                    self.message_warning = "9 - Sem Ocorrência de transporte."
                
            if self.am_id:
                self.am_id.invoice_incoterm_id = self.incoterm_id.id

    @api.onchange("vehicle_id")
    def _onchange_vehicle_id(self):
        if self.vehicle_id and self.carrier_id:
            for vehicle in self.carrier_id.vehicle_ids:
                self.vehicle = vehicle.name
                self.plate = vehicle.plate
                self.rntc_code = vehicle.rntc_code
                self.vehicle_id = vehicle.id
                self.state_id = vehicle.state_id.id            

    @api.onchange("nfe40_transporta")
    def _onchange_nfe40_transporta(self):
        if self.nfe40_transporta:
            carrier = self.env["delivery.carrier"]
            carrier_id = carrier.search([
                ('partner_id', '=', self.nfe40_transporta.id)
            ])
            if not carrier_id:
                prod_id = self.env["product.product"].search([
                    '|', ('name', 'ilike', 'frete'),
                    ('name', 'ilike', 'entrega')
                    ], limit=1)
                if not prod_id:
                    prod_id = self.env["product.product"].search([], limit=1)
                vals = {
                    "name": self.nfe40_transporta.name,
                    "partner_id": self.nfe40_transporta.id,
                    "product_id": prod_id.id,
                }
                carrier_id = carrier.create(vals)
            self.carrier_id = carrier_id.id
            if self.am_id:
                self.am_id.carrier_id = carrier_id.id
            if not self.nfe40_transporta.cnpj_cpf:
                self.message_warning += " ATENÇÃO: Dados da tranportadora sem CNPJ/CPF"
                if not self.nfe40_transporta.inscr_est:
                    self.message_warning += " e sem Inscrição Estadual."
            for vehicle in self.carrier_id.vehicle_ids:
                self.vehicle = vehicle.name
                self.plate = vehicle.plate
                self.rntc_code = vehicle.rntc_code
                self.vehicle_id = vehicle.id
                self.state_id = vehicle.state_id.id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     import pudb;pu.db
    #     res = super().create(vals_list)
    #     # if not res.vehicle_id and res.plate:
    #     #     vehicle = self.env["l10n_br_delivery.carrier.vehicle"].search([
    #     #         ('plate','=', res.plate)
    #     #     ])
    #     #     if not vehicle:
    #     #         vals = {
    #     #             "name": res.vehicle or res.plate,
    #     #             "plate": res.plate,
    #     #             "rntc_code": res.rntc_code or "",
    #     #             "carrier_id": res.carrier_id.id  
    #     #         }
    #     #         vehicle = self.env["l10n_br_delivery.carrier.vehicle"].create(vals)
    #     #     res.vehicle_id = vehicle.id
    #     return res
 
    # def write(self, vals):
    #     import pudb;pu.db
    #     res = super(TranspFrete,self).write(vals)
    #     # if self.am_id and self.incoterm_id:
    #     #     self.am_id.invoice_incoterm_id = self.incoterm_id.id
    #     #     self.am_id.carrier_id = self.carrier_id.id
    #     # if not self.vehicle_id and "plate" in vals:
    #     #     vehicle = self.env["l10n_br_delivery.carrier.vehicle"].search([
    #     #         ('plate','=', self.plate)
    #     #     ])
    #     #     if not vehicle:
    #     #         vals = {
    #     #             "name": self.vehicle or self.plate,
    #     #             "plate": self.plate,
    #     #             "rntc_code": self.rntc_code or "",
    #     #             "carrier_id": self.carrier_id.id  
    #     #         }
    #     #         vehicle = self.env["l10n_br_delivery.carrier.vehicle"].create(vals)
    #     #     else:
    #     #         vehicle.write(vals)
    #     #     self.vehicle_id = vehicle.id
    #     return res