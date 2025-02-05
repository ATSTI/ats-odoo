# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


from erpbrasil.assinatura import certificado as cert

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    def _compute_certificate(self):
        for record in self:
            certificate = False
            if record.sudo().certificate_nfe_id:
                certificate = record.sudo().certificate_nfe_id
            elif record.sudo().certificate_ecnpj_id:
                certificate = record.sudo().certificate_ecnpj_id

            if not certificate:
                # raise ValidationError(
                #     _(
                #         "Certificate not found, you need to inform your e-CNPJ"
                #         " or e-NFe certificate in the Company."
                #     )
                # )
                return True

            record.certificate = certificate

    @api.model
    def _get_br_ecertificate(self, only_ecnpj=False):
        # import pudb;pu.db
        certificate = False
        if self.sudo().certificate_nfe_id or self.sudo().certificate_ecnpj_id:
            certificate = self.certificate
        if only_ecnpj:
            if certificate != self.sudo().certificate_ecnpj_id:
                certificate = self.sudo().certificate_ecnpj_id
                if not certificate:
                    # raise ValidationError(
                        # _("Only e-CNPJ Certicate can be used for this case.")
                    # )
                    return ""
        if certificate:
            return cert.Certificado(
                arquivo=certificate.file,
                senha=certificate.password,
            )
        else:
            return certificate
