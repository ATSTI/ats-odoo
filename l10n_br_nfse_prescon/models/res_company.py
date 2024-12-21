# Copyright 2023 - TODAY, KMEE INFORMATICA LTDA
# Copyright 2023 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    provedor_nfse = fields.Selection(
        selection_add=[
            ("presconnfe", "PresconNFe"),
        ]
    )

    presconnfe_production_token = fields.Char(
        string="PresconNFe Production Token",
    )

    presconnfe_homologation_token = fields.Char(
        string="FocusNFe Homologation Token",
    )

    presconnfe_nfse_service_type_value = fields.Selection(
        [
            ("item_lista_servico", "Service Type"),
            ("codigo_tributacao_municipio", "City Taxation Code"),
        ],
        string="NFSE Service Type Value",
        default="item_lista_servico",
    )

    presconnfe_nfse_cnae_code_value = fields.Selection(
        [
            ("codigo_cnae", "CNAE Code"),
            ("codigo_tributacao_municipio", "City Taxation Code"),
        ],
        string="NFSE CNAE Code Value",
        default="codigo_cnae",
    )

    presconnfe_nfse_wsdl = fields.Char(
        string="URL do WSDL"
    )

    presconnfe_nfse_password = fields.Char(
        string="Prescon - senha"
    )

    presconnfe_nfse_token_validate = fields.Datetime(
        string="Prescon - Token validade"
    )

    presconnfe_nfse_aliquota_iss = fields.Float(
        string="Prescon - aliquota ISS"
    )

    def get_presconnfe_token(self):
        """
        Retrieve the appropriate FocusNFe API token based on the current NFSe
        environment setting.
        Decide between the production and homologation (test) environment tokens by
        examining the 'nfse_environment' field of the record.

        Precondition:
        - Call this method on a single record only. The method uses ensure_one to
        enforce this rule.

        Returns:
        - str: The FocusNFe token. Return the production token if 'nfse_environment'
        is set to "1"; otherwise, return the homologation token.

        Raises:
        - ValueError: If the method is called on a recordset containing more than one
        record.
        """
        self.ensure_one()
        return (
            self.presconnfe_production_token
            if self.nfse_environment == "1"
            else self.presconnfe_homologation_token
        )
