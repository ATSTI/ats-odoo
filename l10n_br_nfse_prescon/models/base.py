# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# com base no codigo do modulo l10n_br_nfse_focus


import requests
import xml.etree.ElementTree as ET

from odoo import _, models
from odoo.exceptions import UserError


class PresconNfseBase(models.AbstractModel):
    _name = "prescon.nfse.base"
    _description = "PRESCON NFSE Base"

    def _make_prescon_nfse_http_request(
        self, method, url, token, code, data=None, service_name="NFSe Prescon"
    ):
        headers = {
           'Authorization': f'{code}-{token}',
           'content-type': 'application/xml',
        }
        try:
            response = requests.request(
                method,
                url,
                data=data,
                headers=headers,
                verify=False
            )
            if response.status_code == 422 or response.status_code != 200:
                msg = response.text
                raise UserError(
                    f"Error communicating with {service_name} service: {msg}"
                )
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            raise UserError(
                _("Error communicating with %(service)s service: %(error)s")
                % {"service": service_name, "error": e}
            ) from e
