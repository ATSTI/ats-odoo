from odoo import fields, api, models


class CondoResidenceVehicles(models.Model):
    _name = "condo.residence.vehicles"
    _description = "Vehicles"

    residence_id = fields.Many2one(
        "condo.residence",
        string="Residência",
        ondelete="cascade",
        required=True,
    )

    possui_veiculo = fields.Boolean(string="Possui Veículo?")

    name = fields.Text("Modelo")

    marca = fields.Char("Marca")

    cor = fields.Char("Cor")

    placa = fields.Char("Placa")

    possui_tag = fields.Boolean("Possui Tag?", default=False)

    numero_tag = fields.Char("Número da Tag")

    quantidade = fields.Integer("Quantidade", default=1)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_residence_tags()
        return records

    def write(self, vals):
        result = super().write(vals)
        self._sync_residence_tags()
        return result

    def _sync_residence_tags(self):
        Tag = self.env["condo.residence.tags"]
        for vehicle in self.filtered(
            lambda v: v.residence_id and v.possui_tag and v.numero_tag
        ):
            existing = Tag.search([
                ("residence_id", "=", vehicle.residence_id.id),
                ("numero_tag", "=", vehicle.numero_tag),
            ], limit=1)
            if not existing:
                Tag.create({
                    "residence_id": vehicle.residence_id.id,
                    "name": f"TAG do veículo - {vehicle.placa or vehicle.name}",
                    "numero_tag": vehicle.numero_tag,
                })