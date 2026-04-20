import json

from odoo import api

from .base import PresconNfseBase
from .constants import API_ENDPOINT_NACIONAL, NFSE_URL
from .helpers import _identify_cpf_cnpj


class PresconNfseNacional(PresconNfseBase):
    """Prescon NFSe Nacional implementation."""

    _name = "prescon.nfse.nacional"
    _description = "Prescon NFSe Nacional"

    def _make_prescon_nfse_http_request(self, method, url, token, code, data=None, params=None):
        return super()._make_prescon_nfse_http_request(
            method, url, token, code, data, params
        )

    @api.model
    def process_prescon_nfse_nacional_document(self, edoc, ref, company, environment):
        import pudb;pu.db
        token = company.prescon_production_token
        code = company.prescon_code
        # data = self._prepare_payload_nacional(edoc, company)
        # payload = data
        url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['envio']}"
        # ref_params = {"ref": ref}
        return self._make_prescon_nfse_http_request(
            "POST", url, token, code, data=edoc
        )

    @api.model
    def query_focus_nfse_nacional_by_ref(self, ref, company, environment):
        """Query NFSe Nacional by reference.

        Args:
            ref (str): The document reference.
            company (recordset): The company record.
            environment (str): The environment (1=production, 2=homologation).

        Returns:
            requests.Response: The response from the NFSe Nacional service.
        """
        token = company.get_focusnfe_token()
        url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['status']}{ref}"
        return self._make_prescon_nfse_http_request("GET", url, token)

    @api.model
    def cancel_focus_nfse_nacional_document(
        self, ref, cancel_reason, company, environment
    ):
        """Cancel an electronic fiscal document for NFSe Nacional.

        Args:
            ref (str): The document reference.
            cancel_reason (str): The reason for cancellation.
            company (recordset): The company record.
            environment (str): The environment (1=production, 2=homologation).

        Returns:
            requests.Response: The response from the NFSe Nacional service.
        """
        token = company.get_focusnfe_token()
        data = {"justificativa": cancel_reason}
        url = f"{NFSE_URL[environment]}{API_ENDPOINT_NACIONAL['cancelamento']}{ref}"
        return self._make_focus_nfse_http_request(
            "DELETE", url, token, data=json.dumps(data)
        )
